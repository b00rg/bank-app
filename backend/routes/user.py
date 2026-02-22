from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.issuing import create_issuing_cardholder
from services.stripe import create_stripe_customer, get_stripe_customer
from services import user_storage
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
        
        user_id = customer_id  # use stripe customer ID as the user_id
        password_hash = hash_password(body.password) if body.password else ""
        overseer_password_hash = hash_password(body.overseer_password) if body.overseer_password else ""

        # Persist to CSV
        user_storage.save_user(
            user_id=user_id,
            name=body.name,
            email=body.email,
            stripe_customer_id=customer_id,
            cardholder_id=cardholder["cardholder_id"],
            password_hash=password_hash,
            overseer_name=body.overseer_name or "",
            overseer_number=body.overseer_number or "",
            overseer_password_hash=overseer_password_hash,
        )

        # Store in session
        request.session["user_id"] = user_id
        request.session["stripe_customer_id"] = customer_id
        request.session["cardholder_id"] = cardholder["cardholder_id"]
        request.session["user_name"] = body.name
        request.session["user_email"] = body.email
        request.session["overseer_name"] = body.overseer_name
        request.session["overseer_number"] = body.overseer_number
        request.session["password_hash"] = password_hash
        request.session["overseer_password_hash"] = overseer_password_hash

        return JSONResponse(content={
            "success": True,
            "user_id": user_id,
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
        # Look up user from CSV first, fall back to session
        csv_user = user_storage.get_user_by_email(body.email)

        if csv_user:
            stored_password_hash = csv_user.get("password_hash", "")
            if stored_password_hash and not verify_password(body.password, stored_password_hash):
                raise HTTPException(status_code=401, detail="Invalid email or password")

            # Restore session from CSV
            request.session["user_id"] = csv_user["user_id"]
            request.session["stripe_customer_id"] = csv_user["stripe_customer_id"]
            request.session["cardholder_id"] = csv_user.get("cardholder_id", "")
            request.session["user_name"] = csv_user["name"]
            request.session["user_email"] = csv_user["email"]
            request.session["overseer_name"] = csv_user.get("overseer_name", "")
            request.session["overseer_number"] = csv_user.get("overseer_number", "")
            request.session["password_hash"] = stored_password_hash
            request.session["overseer_password_hash"] = csv_user.get("overseer_password_hash", "")

            return JSONResponse(content={
                "success": True,
                "user_id": csv_user["user_id"],
                "stripe_customer_id": csv_user["stripe_customer_id"],
                "cardholder_id": csv_user.get("cardholder_id", ""),
                "name": csv_user["name"],
                "email": body.email,
                "bank_linked": bool(csv_user.get("access_token"))
            })

        # Fall back to session-only (legacy)
        stored_email = request.session.get("user_email")
        stored_password_hash = request.session.get("password_hash")

        if not stored_email or stored_email != body.email:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if stored_password_hash and not verify_password(body.password, stored_password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return JSONResponse(content={
            "success": True,
            "user_id": request.session.get("user_id", ""),
            "stripe_customer_id": request.session.get("stripe_customer_id"),
            "cardholder_id": request.session.get("cardholder_id"),
            "name": request.session.get("user_name"),
            "email": body.email,
            "bank_linked": False
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
        # Search CSV for a user with matching overseer number
        csv_user = None
        for u in user_storage.get_all_users():
            if u.get("overseer_number") == body.number:
                csv_user = u
                break

        if csv_user:
            stored_overseer_password_hash = csv_user.get("overseer_password_hash", "")
            if not stored_overseer_password_hash or not verify_password(body.password, stored_overseer_password_hash):
                raise HTTPException(status_code=401, detail="Invalid number or password")

            request.session["is_overseer"] = True
            request.session["overseer_logged_in"] = True
            request.session["overseer_user_id"] = csv_user["user_id"]

            return JSONResponse(content={
                "success": True,
                "number": body.number,
                "user_name": csv_user["name"],
                "user_email": csv_user["email"],
            })

        # Fall back to session-only (legacy)
        stored_overseer_number = request.session.get("overseer_number")
        stored_overseer_password_hash = request.session.get("overseer_password_hash")

        if not stored_overseer_number or not stored_overseer_password_hash:
            raise HTTPException(status_code=401, detail="No overseer account found in system")

        if stored_overseer_number != body.number:
            raise HTTPException(status_code=401, detail="Invalid number or password")

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
