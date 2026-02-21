from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Handles incoming Stripe webhook events.
    Listens for payment_intent.succeeded and payment_intent.payment_failed.
    Voice alert will be triggered here later — for now returns a clear message.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Verify the webhook signature (skip if no secret set, e.g. during local testing)
    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
    else:
        # No secret set — parse payload directly (local testing only)
        import json
        event = json.loads(payload)

    event_type = event.get("type")
    payment_intent = event.get("data", {}).get("object", {})
    amount = payment_intent.get("amount", 0) / 100
    currency = payment_intent.get("currency", "eur").upper()
    customer_id = payment_intent.get("customer")

    # --- Handle payment success ---
    if event_type == "payment_intent.succeeded":
        print(f"✅ Payment succeeded: {amount} {currency} for customer {customer_id}")
        return JSONResponse(content={
            "status": "success",
            "message": f"Payment of {amount} {currency} was successful.",
            "customer_id": customer_id,
            "amount": amount,
            "currency": currency,
            # TODO: trigger ElevenLabs voice alert to user here
            "alma_message": f"Great news! Your payment of {amount} {currency} went through successfully."
        })

    # --- Handle payment failure ---
    elif event_type == "payment_intent.payment_failed":
        failure_reason = payment_intent.get("last_payment_error", {}).get("message", "Unknown error")
        print(f"❌ Payment failed: {amount} {currency} for customer {customer_id}. Reason: {failure_reason}")
        return JSONResponse(content={
            "status": "failed",
            "message": f"Payment of {amount} {currency} failed.",
            "customer_id": customer_id,
            "amount": amount,
            "currency": currency,
            "failure_reason": failure_reason,
            # TODO: trigger ElevenLabs voice alert to user here
            "alma_message": f"I'm sorry, your payment of {amount} {currency} didn't go through. {failure_reason}. Please check your payment details and try again."
        })

    # --- All other events ---
    else:
        print(f"ℹ️ Unhandled event type: {event_type}")
        return JSONResponse(content={"status": "ignored", "event_type": event_type})