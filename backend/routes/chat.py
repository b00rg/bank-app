"""
routes/chat.py

Gemini-powered conversational endpoint that classifies user intent and
dispatches to the appropriate Stripe or TrueLayer service.

Endpoints
---------
POST /api/chat        — main chat turn
GET  /api/chat/state  — inspect session state (debug)

Intent → action mapping
-----------------------
CHECK_BALANCE   → TrueLayer: get_balance on the user's primary account
TRANSFER_DRAFT  → Stores a pending transfer in session (no charge yet)
CONFIRM         → Executes the pending transfer via Stripe
CANCEL          → Clears the pending transfer from session
CLARIFY         → Returns Gemini's clarifying question to the frontend
HELP            → Returns a help blurb
"""

from __future__ import annotations

import os
import stripe
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.gemini import GeminiIntentClient
from dotenv import load_dotenv

from services.truelayer import get_balance, get_accounts
from services.stripe import get_radar_risk
from services.alerts import (
    send_carer_sms,
    build_fraud_alert_message,
    build_large_payment_message,
)

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(tags=["Chat"])

LARGE_PAYMENT_THRESHOLD = 200.0

# ---------------------------------------------------------------------------
# Payee registry
# Mirrors the allowed payees concept from connect.py.
# Add real Stripe Connect account IDs via env vars for person-to-person.
# ---------------------------------------------------------------------------

PAYEE_REGISTRY: list[dict] = [
    {"label": "Tesco",           "type": "merchant", "stripe_account": None},
    {"label": "Lidl",            "type": "merchant", "stripe_account": None},
    {"label": "Dunnes Stores",   "type": "merchant", "stripe_account": None},
    {"label": "Boots",           "type": "merchant", "stripe_account": None},
    {"label": "Pharmacy",        "type": "merchant", "stripe_account": None},
    {"label": "Electric Ireland","type": "merchant", "stripe_account": None},
    {"label": "Irish Water",     "type": "merchant", "stripe_account": None},
    # Person-to-person — set STRIPE_CONNECT_MARY / STRIPE_CONNECT_JOHN in .env
    {"label": "Mary", "type": "person", "stripe_account": os.getenv("STRIPE_CONNECT_MARY", "")},
    {"label": "John", "type": "person", "stripe_account": os.getenv("STRIPE_CONNECT_JOHN", "")},
]


def _get_payee(label: str) -> dict | None:
    label_lower = label.lower()
    for p in PAYEE_REGISTRY:
        if p["label"].lower() == label_lower:
            return p
    return None


def _payee_labels() -> list[str]:
    return [p["label"] for p in PAYEE_REGISTRY]


# ---------------------------------------------------------------------------
# Gemini client (lazy singleton)
# ---------------------------------------------------------------------------

_gemini_client: GeminiIntentClient | None = None


def _get_gemini_client() -> GeminiIntentClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiIntentClient()
    return _gemini_client


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    transcript: str


# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------

def _handle_check_balance(request: Request, intent_data: dict) -> dict:
    token = request.session.get("truelayer_access_token")
    if not token:
        return {
            "assistant_say": (
                "I can't check your balance because your bank account isn't linked. "
                "Please link your bank first."
            ),
            "data": None,
        }

    primary_account_id = request.session.get("primary_account_id")

    if not primary_account_id:
        try:
            resp = get_accounts(access_token=token)
            results = resp.get("results", [])
            if results:
                primary_account_id = results[0]["account_id"]
                request.session["primary_account_id"] = primary_account_id
        except Exception as exc:
            return {
                "assistant_say": f"I had trouble fetching your accounts. Please try again. ({exc})",
                "data": None,
            }

    if not primary_account_id:
        return {
            "assistant_say": "I couldn't find a linked bank account. Please link your bank first.",
            "data": None,
        }

    try:
        balance_resp = get_balance(primary_account_id, access_token=token)
        results = balance_resp.get("results", [])
        if not results:
            return {
                "assistant_say": "I couldn't retrieve your balance right now. Please try again later.",
                "data": balance_resp,
            }
        bal = results[0]
        available = bal.get("available", 0)
        current = bal.get("current", 0)
        currency = bal.get("currency", "EUR")
        return {
            "assistant_say": (
                f"Your available balance is {available:.2f} {currency}, "
                f"and your current balance is {current:.2f} {currency}."
            ),
            "data": bal,
        }
    except Exception as exc:
        return {
            "assistant_say": f"Sorry, I had trouble checking your balance. ({exc})",
            "data": None,
        }


def _handle_transfer_draft(request: Request, intent_data: dict) -> dict:
    payee_label: str = (intent_data.get("payee_label") or "").strip()
    amount: float = float(intent_data.get("amount") or 0)
    currency: str = intent_data.get("currency") or "EUR"

    if not payee_label or not amount:
        return {
            "assistant_say": "I need both a payee and an amount. Who would you like to pay, and how much?",
            "data": None,
        }

    payee = _get_payee(payee_label)
    if not payee:
        labels = ", ".join(_payee_labels())
        return {
            "assistant_say": (
                f"I don't recognise '{payee_label}' as an allowed payee. "
                f"I can send money to: {labels}."
            ),
            "data": None,
        }

    request.session["pending_transfer"] = {
        "payee_label": payee["label"],
        "payee_type": payee["type"],
        "stripe_account": payee.get("stripe_account") or "",
        "amount": amount,
        "currency": currency,
    }

    assistant_say = intent_data.get("assistant_say") or (
        f"I'd like to send {amount:.2f} {currency} to {payee['label']}. "
        "Please say 'confirm' to go ahead, or 'cancel' to stop."
    )
    return {
        "assistant_say": assistant_say,
        "data": {"pending_transfer": request.session["pending_transfer"]},
    }


def _execute_stripe_payment(
    customer_id: str,
    amount_euros: float,
    payee: dict,
    description: str,
    metadata: dict,
) -> dict:
    """
    Creates a Stripe PaymentIntent.
    Person payees use transfer_data for Connect destination charges.
    """
    params: dict = dict(
        amount=int(amount_euros * 100),
        currency="eur",
        customer=customer_id,
        description=description,
        metadata={**metadata, "source": "alma_app"},
    )
    if payee["type"] == "person" and payee.get("stripe_account"):
        params["transfer_data"] = {"destination": payee["stripe_account"]}

    intent = stripe.PaymentIntent.create(**params)

    radar = None
    if intent.latest_charge:
        try:
            radar = get_radar_risk(intent.latest_charge, description)
        except Exception:
            pass

    return {
        "id": intent.id,
        "client_secret": intent.client_secret,
        "amount": amount_euros,
        "status": intent.status,
        "payee_type": payee["type"],
        "radar": radar,
    }


def _handle_confirm(request: Request, intent_data: dict) -> dict:
    pending = request.session.get("pending_transfer")
    if not pending:
        return {
            "assistant_say": "There's no pending payment to confirm. Would you like to make a transfer?",
            "data": None,
        }

    customer_id = request.session.get("stripe_customer_id")
    if not customer_id:
        return {
            "assistant_say": "I couldn't find your account. Please log in and try again.",
            "data": None,
        }

    user_name = request.session.get("user_name", "the account holder")
    carer_phone = request.session.get("carer_phone")
    carer_name = request.session.get("carer_name", "")
    payee_label: str = pending["payee_label"]
    amount_euros: float = float(pending["amount"])

    payee = _get_payee(payee_label)
    if not payee:
        request.session.pop("pending_transfer", None)
        return {
            "assistant_say": f"I couldn't find payee '{payee_label}'. The payment has been cancelled.",
            "data": None,
        }

    try:
        result = _execute_stripe_payment(
            customer_id=customer_id,
            amount_euros=amount_euros,
            payee=payee,
            description=f"Payment to {payee_label}",
            metadata={
                "carer_phone": carer_phone or "",
                "carer_name": carer_name,
                "user_name": user_name,
            },
        )
    except stripe.error.StripeError as exc:
        return {
            "assistant_say": f"I'm sorry, the payment failed: {exc.user_message or str(exc)}",
            "data": None,
        }
    except Exception as exc:
        return {
            "assistant_say": f"Something went wrong with the payment: {exc}",
            "data": None,
        }

    request.session.pop("pending_transfer", None)

    radar = result.get("radar")

    if carer_phone and radar and radar.get("should_alert"):
        send_carer_sms(
            carer_phone=carer_phone,
            message=build_fraud_alert_message(
                user_name, amount_euros, "EUR",
                radar["risk_level"], radar.get("alma_message", ""),
            ),
        )

    if carer_phone and amount_euros >= LARGE_PAYMENT_THRESHOLD:
        send_carer_sms(
            carer_phone=carer_phone,
            message=build_large_payment_message(user_name, amount_euros, "EUR"),
        )

    if radar and radar.get("should_block"):
        assistant_say = radar["alma_message"]
    elif payee["type"] == "person":
        assistant_say = f"Done! I've sent {amount_euros:.2f} EUR to {payee_label}. The transfer is on its way."
    else:
        assistant_say = f"Payment of {amount_euros:.2f} EUR to {payee_label} is set up. All done!"

    return {"assistant_say": assistant_say, "data": result}


def _handle_cancel(request: Request, intent_data: dict) -> dict:
    request.session.pop("pending_transfer", None)
    return {
        "assistant_say": intent_data.get(
            "assistant_say",
            "No problem, I've cancelled that. Is there anything else I can help you with?",
        ),
        "data": None,
    }


def _handle_clarify(intent_data: dict) -> dict:
    return {
        "assistant_say": intent_data.get("assistant_say", "Could you please clarify what you'd like to do?"),
        "data": {"choices": intent_data.get("choices")},
    }


def _handle_help(intent_data: dict) -> dict:
    labels = ", ".join(_payee_labels())
    return {
        "assistant_say": intent_data.get(
            "assistant_say",
            (
                "Here's what I can help you with: check your balance, send money to someone, "
                "or confirm/cancel a transfer. "
                f"I can send money to: {labels}."
            ),
        ),
        "data": None,
    }


# ---------------------------------------------------------------------------
# Main chat endpoint
# ---------------------------------------------------------------------------

@router.post("/api/chat")
async def chat(request: Request, body: ChatRequest):
    """
    Single conversational turn.

    1. Classify intent via Gemini (with automatic fallback + repair).
    2. Dispatch to the appropriate handler.
    3. Return { intent, assistant_say, data, debug }.
    """
    pending_transfer = request.session.get("pending_transfer")

    try:
        client = _get_gemini_client()
        intent_data, debug_info = client.classify_intent(
            transcript=body.transcript,
            payees_allowed=_payee_labels(),
            pending_transfer=pending_transfer,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Gemini unavailable: {exc}")

    intent: str = intent_data.get("intent", "CLARIFY")

    dispatch = {
        "CHECK_BALANCE":  lambda: _handle_check_balance(request, intent_data),
        "TRANSFER_DRAFT": lambda: _handle_transfer_draft(request, intent_data),
        "CONFIRM":        lambda: _handle_confirm(request, intent_data),
        "CANCEL":         lambda: _handle_cancel(request, intent_data),
        "CLARIFY":        lambda: _handle_clarify(intent_data),
        "HELP":           lambda: _handle_help(intent_data),
    }

    handler = dispatch.get(intent)
    result = handler() if handler else {
        "assistant_say": "I'm not sure how to help with that. Could you rephrase?",
        "data": None,
    }

    return JSONResponse(content={
        "intent": intent,
        "assistant_say": result["assistant_say"],
        "data": result.get("data"),
        "debug": debug_info,
    })


# ---------------------------------------------------------------------------
# Debug endpoint
# ---------------------------------------------------------------------------

@router.get("/api/chat/state")
async def get_chat_state(request: Request):
    """Returns chat-relevant session state. Useful during development."""
    return JSONResponse(content={
        "has_stripe_customer": bool(request.session.get("stripe_customer_id")),
        "has_truelayer_token": bool(request.session.get("truelayer_access_token")),
        "primary_account_id": request.session.get("primary_account_id"),
        "pending_transfer": request.session.get("pending_transfer"),
        "carer_linked": bool(request.session.get("carer_phone")),
        "user_name": request.session.get("user_name"),
    })