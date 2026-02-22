from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.issuing import create_issuing_cardholder
from services.stripe import create_stripe_customer, get_stripe_customer
import hashlib

router = APIRouter()


class CreateUserRequest(BaseModel):
    name: str = None
    email: str
    password: str = None
    overseer_name: str = None
    overseer_number: str = None
    overseer_password: str = None


class LoginRequest(BaseModel):
    email: str
    password: str


def hash_password(password: str) -> str:
    """Simple password hashing using PBKDF2 via hashlib"""
    salt = "alma-banking-app"  # In production, use a random salt per user
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed


@router.post("/api/user/create")
async def create_user(request: Request, body: CreateUserRequest):
    """
    Creates a new user with Stripe customer and Issuing cardholder.
    Requires name, email, and password.
    """
    if not body.name:
        raise HTTPException(status_code=400, detail="Name is required for signup")
    
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
        request.session["overseer_name"] = body.overseer_name
        request.session["overseer_number"] = body.overseer_number
        
        # Store hashed password if provided
        if body.password:
            request.session["password_hash"] = hash_password(body.password)
        
        # Store overseer password hash if provided
        if body.overseer_password:
            request.session["overseer_password_hash"] = hash_password(body.overseer_password)
        
        return JSONResponse(content={
            "success": True,
            "stripe_customer_id": customer_id,
            "cardholder_id": cardholder["cardholder_id"],
            "name": body.name,
            "email": body.email,
            "overseer_name": body.overseer_name,
            "overseer_number": body.overseer_number
        })
    except Exception as e:
        print(f"DEBUG: Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.post("/api/user/login")
async def login_user(request: Request, body: LoginRequest):
    """
    Logs in an existing user by verifying email and password.
    Uses session data (in a real app, would check against database).
    """
    try:
        # Check if user exists in session
        stored_email = request.session.get("user_email")
        stored_password_hash = request.session.get("password_hash")
        
        if not stored_email or stored_email != body.email:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if stored_password_hash and not verify_password(body.password, stored_password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        return JSONResponse(content={
            "success": True,
            "stripe_customer_id": request.session.get("stripe_customer_id"),
            "cardholder_id": request.session.get("cardholder_id"),
            "name": request.session.get("user_name"),
            "email": body.email
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error logging in: {str(e)}")


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


# --- Overseer Routes ---

class OverseerLoginRequest(BaseModel):
    number: str
    password: str


@router.post("/api/overseer/login")
async def overseer_login(request: Request, body: OverseerLoginRequest):
    """
    Authenticates overseer by phone number and password.
    Uses a separate password hash for overseer authentication.
    """
    try:
        # In a real app, this would query a database for overseer credentials
        # For now, check if there's a user in session with matching overseer info
        stored_overseer_number = request.session.get("overseer_number")
        stored_overseer_password_hash = request.session.get("overseer_password_hash")
        
        if not stored_overseer_number or not stored_overseer_password_hash:
            raise HTTPException(status_code=401, detail="No overseer account found in system")
        
        if stored_overseer_number != body.number:
            raise HTTPException(status_code=401, detail="Invalid number or password")
        
        # Verify overseer password
        if not verify_password(body.password, stored_overseer_password_hash):
            raise HTTPException(status_code=401, detail="Invalid number or password")
        
        # Set overseer session
        request.session["is_overseer"] = True
        request.session["overseer_logged_in"] = True
        
        return JSONResponse(content={
            "success": True,
            "number": body.number,
            "user_name": request.session.get("user_name"),
            "user_email": request.session.get("user_email"),
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Error logging in overseer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error logging in: {str(e)}")


@router.get("/api/overseer/users")
async def get_overseer_users(request: Request):
    """
    Returns users associated with this overseer.
    """
    if not request.session.get("is_overseer"):
        raise HTTPException(status_code=401, detail="Not authenticated as overseer")
    
    return JSONResponse(content={
        "success": True,
        "users": [{
            "name": request.session.get("user_name"),
            "email": request.session.get("user_email"),
            "cardholder_id": request.session.get("cardholder_id"),
            "stripe_customer_id": request.session.get("stripe_customer_id"),
        }]
    })
