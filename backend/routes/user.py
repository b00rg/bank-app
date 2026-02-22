from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, validator
from services.stripe import create_stripe_customer, get_stripe_customer

router = APIRouter()


# --- Request model ---

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr  # validates email format automatically

    @validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


# --- Routes ---

@router.post("/api/user/create")
async def create_user(request: Request, body: CreateUserRequest):
    """
    Creates a new user:
    1. Creates a Stripe customer in test mode
    2. Stores the Stripe customer ID in the server-side session
    3. Returns the customer ID to the frontend
    """
    try:
        stripe_customer_id = create_stripe_customer(
            name=body.name,
            email=body.email
        )

        request.session["user_name"] = body.name
        request.session["user_email"] = body.email
        request.session["stripe_customer_id"] = stripe_customer_id

        return {
            "success": True,
            "stripe_customer_id": stripe_customer_id,
            "name": body.name,
            "email": body.email,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("/api/user/me")
async def get_current_user(request: Request):
    """
    Returns the current user's info from session.
    Used on page load to check if user is already onboarded.
    """
    stripe_customer_id = request.session.get("stripe_customer_id")

    if not stripe_customer_id:
        raise HTTPException(status_code=404, detail="No user session found")

    try:
        customer = get_stripe_customer(stripe_customer_id)
        return {
            "success": True,
            "stripe_customer_id": stripe_customer_id,
            "name": request.session.get("user_name"),
            "email": request.session.get("user_email"),
            "stripe_customer": customer,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")


@router.post("/api/user/logout")
async def logout(request: Request):
    """
    Clears the session.
    """
    request.session.clear()
    return {"success": True, "message": "Session cleared"}