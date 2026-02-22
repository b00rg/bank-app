from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.issuing import create_issuing_cardholder
from services.stripe import create_stripe_customer, get_stripe_customer

router = APIRouter()


class CreateUserRequest(BaseModel):
    name: str
    email: str



@router.post("/api/user/create")
async def create_user(request: Request, body: CreateUserRequest):
    """
    Creates a new user with Stripe customer and Issuing cardholder.
    """
    try:
        # Create Stripe customer
        customer_id = create_stripe_customer(body.name, body.email)
        print(f"DEBUG: Customer created: {customer_id}")
        
        # Create Issuing cardholder (with mock address for testing)
        address = {
            "line1": "123 Test Street",
            "city": "Dublin",
            "postal_code": "D01 1AA"
        }
        
        cardholder = create_issuing_cardholder(
            name=body.name,
            email=body.email,
            phone="+353871234567",
           
            address=address
        )
        print(f"DEBUG: Cardholder created: {cardholder}")
        
        # Store in session
        request.session["stripe_customer_id"] = customer_id
        request.session["cardholder_id"] = cardholder["cardholder_id"]
        request.session["user_name"] = body.name
        request.session["user_email"] = body.email
        
        return JSONResponse(content={
            "success": True,
            "stripe_customer_id": customer_id,
            "cardholder_id": cardholder["cardholder_id"],
            "name": body.name,
            "email": body.email
        })
    except Exception as e:
        print(f"DEBUG: Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
    
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