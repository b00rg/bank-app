from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import stripe
import os
import json
from dotenv import load_dotenv
from services.stripe import get_radar_risk
from services.alerts import (
    send_carer_sms,
    build_fraud_alert_message,
    build_large_payment_message,
    build_payment_failure_message,
)

load_dotenv()

router = APIRouter()

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
LARGE_PAYMENT_THRESHOLD = float(200)


@router.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Handles incoming Stripe webhook events.
    Fires carer alerts on fraud flags, large payments, and failures.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
    else:
        event = json.loads(payload)

    event_type = event.get("type")
    payment_intent = event.get("data", {}).get("object", {})
    amount = payment_intent.get("amount", 0) / 100
    currency = payment_intent.get("currency", "eur").upper()
    customer_id = payment_intent.get("customer")
    latest_charge = payment_intent.get("latest_charge")

    # Carer info stored in payment metadata
    carer_phone = payment_intent.get("metadata", {}).get("carer_phone")
    carer_name = payment_intent.get("metadata", {}).get("carer_name")
    user_name = payment_intent.get("metadata", {}).get("user_name", "the account holder")

    # --- Payment succeeded ---
    if event_type == "payment_intent.succeeded":
        radar = None

        if latest_charge:
            try:
                radar = get_radar_risk(latest_charge)
            except Exception as e:
                print(f"Radar check failed: {e}")

        # Build Alma's message
        if radar and radar["should_block"]:
            alma_message = radar["alma_message"]
        else:
            alma_message = f"Your payment of {amount} {currency} was successful."

        # Alert carer if fraud flagged
        if carer_phone and radar and radar.get("should_alert"):
            send_carer_sms(
                carer_phone=carer_phone,
                message=build_fraud_alert_message(user_name, amount, currency, radar["risk_level"], radar["alma_message"])
            )

        # Alert carer if large payment
        if carer_phone and amount >= LARGE_PAYMENT_THRESHOLD:
            send_carer_sms(
                carer_phone=carer_phone,
                message=build_large_payment_message(user_name, amount, currency)
            )

        print(f"✅ Payment succeeded: {amount} {currency} | Risk: {radar}")
        return JSONResponse(content={
            "status": "success",
            "amount": amount,
            "currency": currency,
            "customer_id": customer_id,
            "radar": radar,
            "alma_message": alma_message,
            # TODO: pass alma_message to ElevenLabs TTS here
        })

    # --- Payment failed ---
    elif event_type == "payment_intent.payment_failed":
        failure_reason = (
            payment_intent.get("last_payment_error", {}).get("message")
            or "an unknown error"
        )

        alma_message = (
            f"I'm sorry, your payment of {amount} {currency} didn't go through. "
            f"The reason was: {failure_reason}. "
            f"Please check your payment details and try again, or ask someone you trust for help."
        )

        # Alert carer on failure
        if carer_phone:
            send_carer_sms(
                carer_phone=carer_phone,
                message=build_payment_failure_message(user_name, amount, currency, failure_reason)
            )

        print(f"❌ Payment failed: {amount} {currency} | Reason: {failure_reason}")
        return JSONResponse(content={
            "status": "failed",
            "amount": amount,
            "currency": currency,
            "customer_id": customer_id,
            "failure_reason": failure_reason,
            "alma_message": alma_message,
            # TODO: pass alma_message to ElevenLabs TTS here
        })

    else:
        print(f"ℹ️ Unhandled event: {event_type}")
        return JSONResponse(content={"status": "ignored", "event_type": event_type})