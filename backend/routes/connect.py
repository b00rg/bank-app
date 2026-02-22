from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from routes.payments import process_payment, list_payee_labels
from services.alerts import (
    send_carer_sms,
    build_fraud_alert_message,
    build_large_payment_message,
)

router = APIRouter()

LARGE_PAYMENT_THRESHOLD = 200.0


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class PaymentRequest(BaseModel):
    payee_label: str
    amount: float       # euros
    description: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/api/payments/payees")
async def get_payees():
    """
    Returns the list of allowed payee labels.
    Feed this into the Gemini intent classifier as payees_allowed.
    """
    return JSONResponse(content={"payees": list_payee_labels()})


@router.post("/api/payments/create")
async def create_payment(request: Request, body: PaymentRequest):
    """
    Creates a payment for the current user.
    - Merchant payees  → standard Stripe PaymentIntent
    - Person payees    → Stripe Connect Transfer (destination charge)
    Alerts carer on fraud risk or large payments.
    """
    customer_id = request.session.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(status_code=401, detail="No user session found")

    user_name  = request.session.get("user_name", "the account holder")
    carer_phone = request.session.get("carer_phone")
    carer_name  = request.session.get("carer_name", "")

    try:
        result = process_payment(
            customer_id=customer_id,
            amount_euros=body.amount,
            payee_label=body.payee_label,
            description=body.description,
            metadata={
                "carer_phone": carer_phone or "",
                "carer_name": carer_name,
                "user_name": user_name,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")

    radar = result.get("radar")

    # Alert carer on fraud risk
    if carer_phone and radar and radar.get("should_alert"):
        send_carer_sms(
            carer_phone=carer_phone,
            message=build_fraud_alert_message(
                user_name,
                body.amount,
                "EUR",
                radar["risk_level"],
                radar["alma_message"],
            ),
        )

    # Alert carer on large payment
    if carer_phone and body.amount >= LARGE_PAYMENT_THRESHOLD:
        send_carer_sms(
            carer_phone=carer_phone,
            message=build_large_payment_message(user_name, body.amount, "EUR"),
        )

    payee_type = result.get("payee_type", "merchant")
    alma_message = (
        f"I've sent {body.amount} EUR to {body.payee_label}. Transfer is on its way."
        if payee_type == "person"
        else f"I've set up a payment of {body.amount} EUR to {body.payee_label}. Please confirm to proceed."
    )

    return JSONResponse(content={
        "success": True,
        **result,
        "alma_message": alma_message,
    })