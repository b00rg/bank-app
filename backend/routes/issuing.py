from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
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
    phone: str
    line1: str
    city: str
    postal_code: str
    country: str


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
    stripe_customer_id = request.session.get("stripe_customer_id")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")

    if not stripe_customer_id:
        raise HTTPException(status_code=401, detail="No user session found")

    # Prevent duplicate cardholders
    if request.session.get("cardholder_id"):
        return {
            "success": True,
            "message": "Card already exists",
            "cardholder_id": request.session.get("cardholder_id"),
            "card_id": request.session.get("card_id"),
        }

    try:
        cardholder = create_issuing_cardholder(
            name=user_name,
            email=user_email,
            phone=body.phone,
            address={
                "line1": body.line1,
                "city": body.city,
                "postal_code": body.postal_code,
                "country": body.country,
            },
        )

        card = create_virtual_card(cardholder["cardholder_id"])

        request.session["cardholder_id"] = cardholder["cardholder_id"]
        request.session["card_id"] = card["card_id"]

        return {
            "success": True,
            **cardholder,
            **card,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/issuing/card")
async def get_card_details(request: Request):
    card_id = request.session.get("card_id")
    if not card_id:
        raise HTTPException(status_code=404, detail="No card found")

    return {
        "success": True,
        **get_card(card_id)
    }


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
