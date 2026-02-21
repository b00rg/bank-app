import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Initialise Stripe with test mode secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_stripe_customer(name: str, email: str) -> str:
    """
    Creates a new Stripe customer and returns their customer ID.
    Always runs in test mode (determined by the STRIPE_SECRET_KEY starting with sk_test_).
    """
    customer = stripe.Customer.create(
        name=name,
        email=email,
        metadata={"source": "alma_app"}
    )
    return customer.id


def get_stripe_customer(customer_id: str) -> dict:
    """
    Fetches a Stripe customer by ID.
    Returns a dict with id, name, email.
    """
    customer = stripe.Customer.retrieve(customer_id)
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
    }


def get_recent_transactions(customer_id: str, limit: int = 10) -> list:
    """
    Fetches the most recent charges for a Stripe customer.
    Returns a list of dicts with amount, currency, description, status, and date.
    """
    charges = stripe.Charge.list(customer=customer_id, limit=limit)
    return [
        {
            "id": charge.id,
            "amount": charge.amount / 100,  # Convert cents to euros/pounds
            "currency": charge.currency.upper(),
            "description": charge.description or "Payment",
            "status": charge.status,
            "date": charge.created,  # Unix timestamp
        }
        for charge in charges.data
    ]


def create_payment_intent(customer_id: str, amount_euros: float, description: str) -> dict:
    """
    Creates a Stripe PaymentIntent for a given customer.
    Amount is in euros (converted to cents internally).
    Returns client_secret and payment_intent id.
    """
    intent = stripe.PaymentIntent.create(
        amount=int(amount_euros * 100),  # Stripe expects cents
        currency="eur",
        customer=customer_id,
        description=description,
        metadata={"source": "alma_app"}
    )
    return {
        "id": intent.id,
        "client_secret": intent.client_secret,
        "amount": amount_euros,
        "status": intent.status,
    }