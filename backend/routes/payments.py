from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv
from services.stripe import create_payment_intent, get_radar_risk
from services.alerts import (
    send_carer_sms,
    build_fraud_alert_message,
    build_large_payment_message,
)
from services import user_storage, transaction_storage

load_dotenv()

router = APIRouter()

LARGE_PAYMENT_THRESHOLD = float(200)


# --- Request models ---

class CreatePaymentRequest(BaseModel):
    amount: float        # in euros
    description: str


# --- Routes ---

@router.post("/api/payments/create")
async def create_payment(request: Request, body: CreatePaymentRequest):
    """
    Creates a Stripe PaymentIntent for the current user.
    Checks Radar fraud score and alerts carer if needed.
    """
    customer_id = request.session.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(status_code=401, detail="No user session found")

    user_name = request.session.get("user_name", "the account holder")
    carer_phone = request.session.get("carer_phone")
    carer_name = request.session.get("carer_name", "")

    try:
        # FIX 1: pass carer + user info so webhooks can alert without session
        result = create_payment_intent(
            customer_id=customer_id,
            amount_euros=body.amount,
            description=body.description,
            metadata={
                "carer_phone": carer_phone or "",
                "carer_name": carer_name,
                "user_name": user_name,
            }
        )

        radar = result.get("radar")

        # FIX 2: alert carer on fraud-flagged payments created here, not just via webhook
        if carer_phone and radar and radar.get("should_alert"):
            send_carer_sms(
                carer_phone=carer_phone,
                message=build_fraud_alert_message(
                    user_name,
                    body.amount,
                    "EUR",
                    radar["risk_level"],
                    radar["alma_message"]
                )
            )

        # Alert carer if large payment
        if carer_phone and body.amount >= LARGE_PAYMENT_THRESHOLD:
            send_carer_sms(
                carer_phone=carer_phone,
                message=build_large_payment_message(user_name, body.amount, "EUR")
            )

        alma_message = (
            radar["alma_message"]
            if radar
            else f"I've set up a payment of {body.amount} EUR. Please confirm to proceed."
        )

        return JSONResponse(content={
            "success": True,
            **result,
            "alma_message": alma_message
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")


@router.post("/api/payments/test-radar")
async def test_radar(request: Request):
    """
    TEST ONLY — Creates a real Stripe charge using a test card and returns the Radar score.
    Swap card number to test different risk levels:
      tok_visa                          = normal risk
      tok_visa_chargeDeclinedFraudulent = highest risk / blocked

    Or set FORCE_RISK_LEVEL=elevated|highest in .env to override score without changing token.
    """
    customer_id = request.session.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(status_code=401, detail="No user session found. Create a user first via /api/user/create")

    user_name = request.session.get("user_name", "the account holder")
    carer_phone = request.session.get("carer_phone")

    # --- Swap this token to test different risk levels ---
    test_token = "tok_visa"                # normal risk
    # test_token = "tok_visa_chargeDeclinedFraudulent"  # highest risk / blocked

    try:
        intent = stripe.PaymentIntent.create(
            amount=5000,  # €50
            currency="eur",
            customer=customer_id,
            payment_method_data={
                "type": "card",
                "card": {"token": test_token},
            },
            confirm=True,
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"
            },
        )

        radar = None
        if intent.latest_charge:
            radar = get_radar_risk(intent.latest_charge)

        if carer_phone and radar and radar.get("should_alert"):
            send_carer_sms(
                carer_phone=carer_phone,
                message=build_fraud_alert_message(
                    user_name,
                    50.0,
                    "EUR",
                    radar["risk_level"],
                    radar["alma_message"]
                )
            )

        return JSONResponse(content={
            "success": True,
            "payment_intent_id": intent.id,
            "status": intent.status,
            "test_token_used": test_token,
            "radar": radar,
            "whatsapp_alert_sent": bool(carer_phone and radar and radar.get("should_alert")),
            "alma_message": radar["alma_message"] if radar else "Payment processed."
        })

    except stripe.error.CardError as e:
        return JSONResponse(content={
            "success": False,
            "status": "declined",
            "test_token_used": test_token,
            "decline_reason": e.user_message,
            "alma_message": f"This payment was blocked. {e.user_message}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


# --- Platform user-to-user transfers ---

class SendToUserRequest(BaseModel):
    sender_user_id: str
    recipient_user_id: str
    amount: float
    currency: str = "GBP"
    description: str = ""


@router.post("/api/payments/send-to-user")
async def send_to_user(body: SendToUserRequest):
    """
    Send money to another platform user.
    Records an outgoing transaction for the sender and an incoming one for the recipient.
    Both appear in each user's platform transaction history.
    """
    if body.sender_user_id == body.recipient_user_id:
        raise HTTPException(status_code=400, detail="Cannot send money to yourself")

    sender = user_storage.get_user(body.sender_user_id)
    if not sender:
        raise HTTPException(status_code=404, detail="Sender account not found")

    recipient = user_storage.get_user(body.recipient_user_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient account not found")

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    description = body.description.strip() if body.description else ""

    transaction_storage.record_transaction(
        user_id=body.sender_user_id,
        transaction_type="SENT",
        amount=body.amount,
        currency=body.currency,
        from_account_id=body.sender_user_id,
        to_account_id=body.recipient_user_id,
        description=description or f"Sent to {recipient['name']}",
        status="COMPLETED",
    )

    transaction_storage.record_transaction(
        user_id=body.recipient_user_id,
        transaction_type="RECEIVED",
        amount=body.amount,
        currency=body.currency,
        from_account_id=body.sender_user_id,
        to_account_id=body.recipient_user_id,
        description=description or f"Received from {sender['name']}",
        status="COMPLETED",
    )

    return {
        "success": True,
        "message": f"Sent {body.currency} {body.amount:.2f} to {recipient['name']}",
        "sender": sender["name"],
        "recipient": recipient["name"],
        "amount": body.amount,
        "currency": body.currency,
    }


@router.get("/api/payments/platform-history")
async def platform_history(user_id: str = Query(...), limit: int = Query(50, ge=1, le=500)):
    """
    Returns platform transaction history (sent/received) for a user.
    No session auth required — intended for the onboarding dashboard.
    """
    user = user_storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = transaction_storage.get_user_transactions(user_id, limit=limit)
    return {"transactions": transactions, "count": len(transactions)}