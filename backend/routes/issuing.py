from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from services.issuing import (
    create_issuing_cardholder,
    create_virtual_card,
    get_card,
    update_spending_limit,
    freeze_card,
    unfreeze_card,
    get_card_transactions,
)

router = APIRouter()

# -------------------------
# Request Models
# -------------------------

class CreateCardRequest(BaseModel):
    phone: str = None
    line1: str = None
    city: str = None
    postal_code: str = None
    country: str = None
    weekly_limit_euros: float = 100.0  # Default limit
    expiration_months: int = 12
    billing_address: str = ""
    billing_city: str = ""
    billing_postal: str = ""
    blocked_categories: list = []


class CardActionRequest(BaseModel):
    card_id: str


class UpdateLimitRequest(BaseModel):
    card_id: str
    weekly_limit_euros: float


# -------------------------
# Routes
# -------------------------


@router.post("/api/issuing/card/create")
async def create_card(request: Request, body: CreateCardRequest):
    """
    Creates a virtual card for the user with specified spending limit.
    Requires cardholder_id in session.
    """
    if not request.session.get("stripe_customer_id"):
        raise HTTPException(status_code=401, detail="No user session found")

    cardholder_id = request.session.get("cardholder_id")
    if not cardholder_id:
        raise HTTPException(status_code=400, detail="No cardholder found. Complete onboarding first.")

    try:
        card = create_virtual_card(cardholder_id)
        
        # Set spending limit if provided
        if body.weekly_limit_euros > 0:
            update_spending_limit(card["card_id"], body.weekly_limit_euros)
        
        request.session["card_id"] = card["card_id"]
        request.session["card_expiration_months"] = body.expiration_months
        request.session["card_billing_address"] = body.billing_address
        request.session["card_billing_city"] = body.billing_city
        request.session["card_billing_postal"] = body.billing_postal
        request.session["card_blocked_categories"] = body.blocked_categories
        
        return JSONResponse(content={
            "success": True,
            "card_id": card["card_id"],
            "last4": card["last4"],
            "status": card["status"],
            "spending_limit": body.weekly_limit_euros,
            "expiration_months": body.expiration_months,
            "billing_address": body.billing_address,
            "billing_city": body.billing_city,
            "blocked_categories": body.blocked_categories,
            "alma_message": f"Your virtual card {card['last4']} is ready to use!"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating card: {str(e)}")


@router.get("/api/issuing/card")
async def get_card_details(request: Request):
    """
    Returns current card details.
    """
    if not request.session.get("stripe_customer_id"):
        raise HTTPException(status_code=401, detail="No user session found")

    card_id = request.session.get("card_id")
    if not card_id:
        raise HTTPException(status_code=404, detail="No card found")

    try:
        card = get_card(card_id)
        return JSONResponse(content=card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching card: {str(e)}")


@router.post("/api/issuing/card/freeze")
async def freeze(request: Request, body: CardActionRequest):
    try:
        return {"success": True, **freeze_card(body.card_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Freeze card failed: {str(e)}")


@router.post("/api/issuing/card/unfreeze")
async def unfreeze(request: Request, body: CardActionRequest):
    try:
        return {"success": True, **unfreeze_card(body.card_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unfreeze card failed: {str(e)}")


@router.post("/api/issuing/card/limit")
async def update_limit(request: Request, body: UpdateLimitRequest):
    try:
        return {"success": True, **update_spending_limit(body.card_id, body.weekly_limit_euros)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update limit failed: {str(e)}")


@router.get("/api/issuing/card/transactions")
async def transactions(request: Request):
    card_id = request.session.get("card_id")
    if not card_id:
        raise HTTPException(status_code=404, detail="No card found")

    return {
        "success": True,
        "transactions": get_card_transactions(card_id)
    }

