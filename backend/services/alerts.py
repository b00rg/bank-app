from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Twilio shared sandbox number


def send_carer_sms(carer_phone: str, message: str) -> bool:
    """
    Sends a WhatsApp message to the carer via Twilio sandbox.
    Carer must have opted in by messaging the sandbox number first.
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
        print(f"⚠️ No Twilio credentials — message would have been: {message}")
        return False

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{carer_phone}"  # e.g. whatsapp:+353871234567
        )
        print(f"💬 WhatsApp sent to {carer_phone}")
        return True

    except Exception as e:
        print(f"❌ Failed to send WhatsApp: {e}")
        return False


def build_fraud_alert_message(user_name: str, amount: float, currency: str, risk_level: str, alma_message: str) -> str:
    return (
        f"🚨 ALMA ALERT\n"
        f"{user_name} made a payment of {amount} {currency} "
        f"flagged as {risk_level.upper()} risk.\n\n"
        f"{alma_message}"
    )


def build_large_payment_message(user_name: str, amount: float, currency: str) -> str:
    return (
        f"💸 ALMA ALERT\n"
        f"{user_name} just made a large payment of {amount} {currency}. "
        f"Please check in with them if this seems unexpected."
    )


def build_payment_failure_message(user_name: str, amount: float, currency: str, reason: str) -> str:
    return (
        f"⚠️ ALMA ALERT\n"
        f"{user_name}'s payment of {amount} {currency} failed.\n"
        f"Reason: {reason}\n"
        f"They may need your help."
    )


def build_registration_message(user_name: str) -> str:
    return (
        f"👋 Hi! You've been added as a trusted contact for {user_name} on Alma.\n\n"
        f"You'll receive WhatsApp alerts if a payment looks suspicious, "
        f"fails, or is unusually large."
    )