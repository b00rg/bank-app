import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- VALIDATED STRIPE CATEGORY IDS ---
BLOCKED_CATEGORIES = [
    "betting_casino_gambling",    # Blocks gambling
    "dating_escort_services",     # Blocks romance scams
    "cigar_stores_and_stands",    # Blocks tobacco
]

DEFAULT_WEEKLY_LIMIT = int(os.getenv("DEFAULT_WEEKLY_LIMIT", 50000))  # €500 in cents


def create_issuing_cardholder(name: str, email: str, phone: str, address: dict) -> dict:
    """Creates a Stripe Issuing cardholder (Ireland-safe version)."""

    parts = name.strip().split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else "User"

    # FIX: For Ireland, provide a valid county in 'state'
    billing_address = {
        "line1": address["line1"],
        "city": address["city"],
        "postal_code": address["postal_code"].upper().replace(" ", ""),
        "country": "IE",
        "state": "Dublin",   # REQUIRED for Ireland
    }

    cardholder = stripe.issuing.Cardholder.create(
        type="individual",
        name=name,
        individual={
            "first_name": first_name,
            "last_name": last_name,
        },
        email=email,
        phone_number=phone,
        billing={
            "address": billing_address
        },
        metadata={"source": "alma_app"},
    )

    return {
        "cardholder_id": cardholder.id,
        "name": name,
        "email": email,
        "status": cardholder.status,
    }


def create_virtual_card(cardholder_id: str, weekly_limit: int = None) -> dict:
    limit = weekly_limit or DEFAULT_WEEKLY_LIMIT

    card = stripe.issuing.Card.create(
        cardholder=cardholder_id,
        currency="eur",
        type="virtual",
        status="active",
        spending_controls={
            "blocked_categories": BLOCKED_CATEGORIES,
            "spending_limits": [
                {
                    "amount": limit,
                    "interval": "weekly",
                }
            ],
        },
        metadata={"source": "alma_app"}
    )
    return {
        "card_id": card.id,
        "last4": card.last4,
        "exp_month": card.exp_month,
        "exp_year": card.exp_year,
        "status": card.status,
        "brand": card.brand,
        "spending_controls": card.spending_controls,
    }


def get_card(card_id: str) -> dict:
    card = stripe.issuing.Card.retrieve(card_id)
    return {
        "card_id": card.id,
        "last4": card.last4,
        "exp_month": card.exp_month,
        "exp_year": card.exp_year,
        "status": card.status,
        "brand": card.brand,
        "spending_controls": card.spending_controls,
    }

def freeze_card(card_id: str) -> dict:
    """Freeze a virtual card (set inactive)."""
    try:
        card = stripe.issuing.Card.modify(card_id, status="inactive")
        return {
            "card_id": card.id,
            "last4": card.last4,
            "status": card.status,
            "frozen": True,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe API error (freeze): {e.user_message or str(e)}")


def unfreeze_card(card_id: str) -> dict:
    """Unfreeze a virtual card (set active)."""
    try:
        card = stripe.issuing.Card.modify(card_id, status="active")
        return {
            "card_id": card.id,
            "last4": card.last4,
            "status": card.status,
            "frozen": False,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe API error (unfreeze): {e.user_message or str(e)}")


def update_spending_limit(card_id: str, weekly_limit_euros: float) -> dict:
    """Update the weekly spending limit on a card."""
    try:
        card = stripe.issuing.Card.modify(
            card_id,
            spending_controls={
                "spending_limits": [
                    {
                        "amount": int(weekly_limit_euros * 100),
                        "interval": "weekly",
                        "categories": [],
                    }
                ],
                "blocked_categories": BLOCKED_CATEGORIES,
            }
        )
        return {
            "card_id": card.id,
            "last4": card.last4,
            "status": card.status,
            "spending_controls": card.spending_controls,
            "new_weekly_limit_euros": weekly_limit_euros,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe API error (update limit): {e.user_message or str(e)}")


def get_card_transactions(card_id: str, limit: int = 10) -> list:
    from datetime import datetime, timezone
    transactions = stripe.issuing.Transaction.list(card=card_id, limit=limit)
    
    return [
        {
            "id": txn.id,
            "amount": abs(txn.amount) / 100,
            "currency": txn.currency.upper(),
            "merchant": txn.merchant_data.name if txn.merchant_data else "Unknown",
            "merchant_category": txn.merchant_data.category if txn.merchant_data else None,
            "date": datetime.fromtimestamp(txn.created, tz=timezone.utc).isoformat(),
            "type": txn.type,
        }
        for txn in transactions.data
    ]
