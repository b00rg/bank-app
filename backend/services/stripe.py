import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Initialise Stripe with test mode secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Radar risk thresholds
RISK_SCORE_ELEVATED = 50   # alert carer above this
RISK_SCORE_HIGHEST = 75    # block and alert above this

# Demo flag — set to "normal", "elevated", or "highest" to force a risk level for testing
# Set to None in production
FORCE_RISK_LEVEL = os.getenv("FORCE_RISK_LEVEL", None)

# Suspicious activity patterns specific to elderly/disability users
SUSPICIOUS_PATTERNS = [
    "gift card",
    "itunes",
    "google play",
    "amazon gift",
    "wire transfer",
    "western union",
    "moneygram",
    "cryptocurrency",
    "bitcoin",
    "urgent",
    "emergency transfer",
    "hmrc",
    "revenue",
    "refund overpayment",
    "lottery",
    "prize",
    "inheritance",
    "investment opportunity",
    "guaranteed returns",
    "act now",
    "limited time",
    "verify your account",
    "suspended account",
]


def create_stripe_customer(name: str, email: str) -> str:
    customer = stripe.Customer.create(
        name=name,
        email=email,
        metadata={"source": "alma_app"}
    )
    return customer.id


def get_stripe_customer(customer_id: str) -> dict:
    customer = stripe.Customer.retrieve(customer_id)
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
    }


def get_recent_transactions(customer_id: str, limit: int = 10) -> list:
    charges = stripe.Charge.list(customer=customer_id, limit=limit)
    return [
        {
            "id": charge.id,
            "amount": charge.amount / 100,
            "currency": charge.currency.upper(),
            "description": charge.description or "Payment",
            "status": charge.status,
            "date": charge.created,
            "risk_level": charge.outcome.risk_level if charge.outcome else "unknown",
            "risk_score": charge.outcome.risk_score if charge.outcome else None,
        }
        for charge in charges.data
    ]


def check_suspicious_description(description: str) -> tuple[bool, str]:
    """
    Checks payment description against known scam patterns
    that specifically target elderly and disabled users.
    Returns (is_suspicious, matched_pattern).
    """
    if not description:
        return False, None

    description_lower = description.lower()
    for pattern in SUSPICIOUS_PATTERNS:
        if pattern in description_lower:
            return True, pattern

    return False, None


def build_risk_response(risk_level: str, risk_score: int, suspicious_pattern: str = None) -> dict:
    """
    Builds the risk response dict with alma_message, should_block, and should_alert.
    """
    if suspicious_pattern and risk_level == "normal":
        risk_level = "elevated"

    if risk_level == "highest" or (risk_score and risk_score >= RISK_SCORE_HIGHEST):
        if suspicious_pattern:
            alma_message = (
                f"I'm very concerned about this payment. "
                f"It mentions '{suspicious_pattern}' which is commonly used in scams targeting people like you. "
                f"I have blocked it to keep you safe. "
                f"Please speak to someone you trust before trying again."
            )
        else:
            alma_message = (
                "I'm very concerned about this payment. "
                "Our fraud detection has flagged it as high risk and I have blocked it to keep you safe. "
                "If someone has asked you to make this payment, please speak to a trusted person first."
            )
        should_block = True
        should_alert = True

    elif risk_level == "elevated" or (risk_score and risk_score >= RISK_SCORE_ELEVATED):
        if suspicious_pattern:
            alma_message = (
                f"This payment looks suspicious to me. "
                f"It mentions '{suspicious_pattern}' which is often used in scams. "
                f"I've let your trusted contact know. "
                f"Please double-check before going ahead."
            )
        else:
            alma_message = (
                "This payment looks a little unusual to me. "
                "I've let your trusted contact know, but you can still go ahead if you're sure. "
                "Please take a moment to double-check before confirming."
            )
        should_block = False
        should_alert = True

    else:
        alma_message = "This payment looks fine. Would you like to go ahead?"
        should_block = False
        should_alert = False

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "should_block": should_block,
        "should_alert": should_alert,
        "suspicious_pattern": suspicious_pattern,
        "alma_message": alma_message,
    }


def get_radar_risk(charge_id: str, description: str = None) -> dict:
    """
    Retrieves the Stripe Radar fraud score for a specific charge.
    Also checks description against disability-specific scam patterns.
    If FORCE_RISK_LEVEL is set, overrides Stripe score for testing.
    """
    if FORCE_RISK_LEVEL:
        risk_level = FORCE_RISK_LEVEL
        risk_score = {"normal": 10, "elevated": 60, "highest": 85}.get(FORCE_RISK_LEVEL, 10)
    else:
        charge = stripe.Charge.retrieve(charge_id)
        outcome = charge.outcome
        risk_level = outcome.risk_level if outcome else "unknown"
        risk_score = outcome.risk_score if outcome else None
        if not description and charge.description:
            description = charge.description

    is_suspicious, matched_pattern = check_suspicious_description(description)

    return build_risk_response(risk_level, risk_score, matched_pattern)


def create_payment_intent(
    customer_id: str,
    amount_euros: float,
    description: str,
    metadata: dict = None,  # FIX: accept extra metadata (carer info, user name)
) -> dict:
    """
    Creates a Stripe PaymentIntent for a given customer.
    Checks description for suspicious patterns before creating.
    Stores carer info in metadata so webhooks can alert without needing a session.
    """
    is_suspicious, matched_pattern = check_suspicious_description(description)

    # Merge caller metadata with source tag
    combined_metadata = {"source": "alma_app"}
    if metadata:
        combined_metadata.update(metadata)

    intent = stripe.PaymentIntent.create(
        amount=int(amount_euros * 100),
        currency="eur",
        customer=customer_id,
        description=description,
        metadata=combined_metadata,  # FIX: was always just {"source": "alma_app"}
    )

    radar = None
    if intent.latest_charge:
        try:
            radar = get_radar_risk(intent.latest_charge, description)
        except Exception:
            pass
    elif is_suspicious:
        radar = build_risk_response("elevated", None, matched_pattern)

    return {
        "id": intent.id,
        "client_secret": intent.client_secret,
        "amount": amount_euros,
        "status": intent.status,
        "radar": radar,
    }