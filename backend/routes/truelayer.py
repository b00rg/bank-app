from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from backend.services import truelayer
from backend.services import user_storage
from backend.services import transaction_storage

router = APIRouter(prefix="/api/truelayer", tags=["TrueLayer"])


class OnboardUserRequest(BaseModel):
    """Initial user onboarding with personal info."""
    user_id: str
    name: str
    email: str
    phone: str = ""


class LinkBankRequest(BaseModel):
    """Request to link user's bank account."""
    user_id: str
    auth_code: str


class PaymentRequest(BaseModel):
    """Request to initiate a payment."""
    amount: float
    currency: str
    beneficiary_name: str
    beneficiary_account: str


class TransferRequest(BaseModel):
    """Request to initiate a transfer."""
    amount: float
    currency: str
    from_account_id: str
    to_account_id: str
    reference: str = ""


@router.get("/users")
async def get_all_users():
    """
    Get all users from CSV with their basic info.
    Used for user selection in the UI.
    
    Returns:
        dict with list of users
    """
    users = user_storage.get_all_users()
    
    # Format users for frontend
    formatted_users = []
    for user in users:
        formatted_users.append({
            "user_id": user.get("user_id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "bank_linked": bool(user.get("access_token")),
            "primary_account_name": user.get("primary_account_name"),
            "created_at": user.get("created_at")
        })
    
    return {"users": formatted_users}


@router.post("/onboard")
async def onboard_user(request: OnboardUserRequest):
    """
    STEP 1: Create new user account with personal info.
    Saves user data to CSV.
    
    Args:
        user_id: Unique user identifier
        name: User's full name
        email: User's email
        phone: User's phone number
    
    Returns:
        dict with user_id and next_step instructions
    """
    # Check if user already exists
    existing_user = user_storage.get_user(request.user_id)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"User {request.user_id} already exists"
        )
    
    # Save user to CSV
    user_storage.save_user(
        user_id=request.user_id,
        name=request.name,
        email=request.email,
        phone=request.phone
    )
    
    return {
        "status": "user_created",
        "user_id": request.user_id,
        "message": "User created successfully",
        "next_step": "GET /api/truelayer/auth-url to link bank account"
    }


@router.get("/auth-url")
async def get_auth_url():
    """
    STEP 2: Get the TrueLayer OAuth authorization URL.
    User should be redirected to this URL to link their bank.
    
    Returns:
        dict with 'auth_url' for user to visit
    """
    auth_url = truelayer.get_authorization_url()
    return {
        "auth_url": auth_url,
        "message": "Redirect user to this URL to authorize bank access"
    }


@router.post("/link-bank")
async def link_bank(request: LinkBankRequest):
    """
    STEP 3: Link user's bank account via TrueLayer OAuth.
    Exchanges auth code for access token and stores it.
    
    Args:
        user_id: Your app's user ID
        auth_code: Authorization code from TrueLayer callback
    
    Returns:
        dict with access_token, accounts, and user data
    """
    # Check if user exists
    user = user_storage.get_user(request.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {request.user_id} not found. Call /onboard first."
        )
    
    # Exchange auth code for access token
    result = truelayer.link_user_bank(request.user_id, request.auth_code)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Extract primary account
    accounts = result.get("accounts", {}).get("results", [])
    primary_account_id = accounts[0]["account_id"] if accounts else ""
    primary_account_name = accounts[0].get("display_name", "") if accounts else ""
    
    # Update user with token and account info
    user_storage.save_user(
        user_id=request.user_id,
        name=user.get("name", ""),
        email=user.get("email", ""),
        phone=user.get("phone", ""),
        access_token=result.get("access_token", ""),
        token_type=result.get("token_type", "Bearer"),
        expires_in=result.get("expires_in", 0),
        primary_account_id=primary_account_id,
        primary_account_name=primary_account_name
    )
    
    return {
        "status": "bank_linked",
        "user_id": request.user_id,
        "access_token": result.get("access_token"),
        "accounts": accounts,
        "message": "Bank account linked successfully",
        "next_step": "GET /api/truelayer/accounts to fetch all accounts"
    }


@router.get("/user/{user_id}")
async def get_user_profile(user_id: str):
    """
    Get user profile and saved data.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        dict: User profile data
    """
    user = user_storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "access_token": user["access_token"],
        "primary_account_id": user["primary_account_id"],
        "primary_account_name": user["primary_account_name"],
        "bank_linked": bool(user["access_token"]),
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


@router.get("/accounts")
async def get_accounts(authorization: str = Header(None)):
    """
    Fetch all linked bank accounts.
    Uses access token from Authorization header (Bearer token).
    
    Returns:
        list of accounts with account_id, name, type, currency
    """
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.replace("Bearer ", "")
    accounts = truelayer.get_accounts(access_token=token)
    return accounts


@router.get("/accounts/{account_id}/transactions")
async def get_transactions(account_id: str, limit: int = Query(20, ge=1, le=100), authorization: str = Header(None)):
    """
    Fetch transactions for a specific account.
    Uses access token from Authorization header (Bearer token).
    
    Args:
        account_id: The account ID
        limit: Number of transactions to fetch (1-100, default 20)
    
    Returns:
        list of transactions with amount, date, description, status
    """
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.replace("Bearer ", "")
    transactions = truelayer.get_transactions(account_id, access_token=token)
    return transactions


@router.get("/accounts/{account_id}/balance")
async def get_balance(account_id: str, authorization: str = Header(None)):
    """
    Fetch balance for a specific account.
    Uses access token from Authorization header (Bearer token).
    
    Args:
        account_id: The account ID
    
    Returns:
        dict with available and current balance
    """
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.replace("Bearer ", "")
    balance = truelayer.get_balance(account_id, access_token=token)
    return balance


@router.post("/payments/initiate")
async def initiate_payment(request: PaymentRequest, authorization: str = Header(None), user_id: str = Query(None)):
    """
    Initiate a bank payment via TrueLayer Payments API.
    
    Verifies the user has a valid access token, then uses client credentials
    to obtain a payments token for actual payment initiation.
    
    Args:
        amount: Payment amount
        currency: Currency code (e.g., 'GBP', 'EUR')
        beneficiary_name: Recipient name
        beneficiary_account: Recipient account number/IBAN
        user_id: User ID for transaction recording
    
    Returns:
        dict with payment confirmation and status
    """
    # Verify user has valid access token (for authorization only)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    # Verify user exists and has this token in CSV
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    user = user_storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    if user.get("access_token") != token:
        raise HTTPException(status_code=403, detail="Token does not match this user")
    
    # Call payment initiation (uses client credentials internally)
    result = truelayer.initiate_payment(
        request.amount,
        request.currency,
        request.beneficiary_name,
        request.beneficiary_account
    )
    
    # Record payment transaction if user_id provided and payment was initiated
    if user_id and "error" not in result:
        payment_id = result.get("id") or result.get("payment_id")
        if payment_id:
            transaction_storage.record_transaction(
                user_id=user_id,
                transaction_type="payment",
                amount=request.amount,
                currency=request.currency,
                status="initiated",
                details=f"Payment to {request.beneficiary_name} ({request.beneficiary_account})",
                transaction_id=payment_id
            )
        
    
    return result


@router.post("/transfers/initiate")
async def initiate_transfer(request: TransferRequest, authorization: str = Header(None), user_id: str = Query(None)):
    """
    Initiate a transfer between accounts.
    Uses access token from Authorization header (Bearer token).
    Records the transaction in transaction history.
    
    Args:
        amount: Transfer amount
        currency: Currency code (e.g., 'GBP', 'EUR')
        from_account_id: Source account ID
        to_account_id: Destination account ID
        reference: Transfer reference/description
        user_id (query param): User ID for transaction recording
    
    Returns:
        dict with transfer confirmation and status
    """
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    # Verify user exists and has this token in CSV
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    user = user_storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    if user.get("access_token") != token:
        raise HTTPException(status_code=403, detail="Token does not match this user")
    result = truelayer.initiate_transfer(
        request.amount,
        request.currency,
        request.from_account_id,
        request.to_account_id,
        request.reference,
        access_token=token
    )
    
    # Record transaction if user_id is provided and transfer is successful
    if user_id and "error" not in result:
        transaction_storage.record_transaction(
            user_id=user_id,
            transaction_type="TRANSFER",
            amount=request.amount,
            currency=request.currency,
            from_account_id=request.from_account_id,
            to_account_id=request.to_account_id,
            description=request.reference,
            status="PENDING"
        )
    
    return result


@router.get("/transactions")
async def get_user_transactions(user_id: str = Query(...), limit: int = Query(50, ge=1, le=500), authorization: str = Header(None)):
    """
    Get transaction history for a user.
    Requires valid Bearer token for authorization.
    
    Args:
        user_id: User's unique identifier
        limit: Maximum number of transactions to return (1-500, default 50)
        authorization: Bearer token for authentication
    
    Returns:
        dict with list of transactions
    """
    # Verify Bearer token is present
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    # Verify user exists and has this token
    user = user_storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    if user.get("access_token") != token:
        raise HTTPException(status_code=403, detail="Token does not match this user")
    
    transactions = transaction_storage.get_user_transactions(user_id, limit=limit)
    return {
        "user_id": user_id,
        "transactions": transactions,
        "count": len(transactions)
    }


@router.get("/callback")
async def oauth_callback(code: str = Query(...), state: str = Query(None)):
    """
    OAuth callback endpoint from TrueLayer.
    User is redirected here after approving bank access.
    Frontend should capture the code and call /link-bank.
    
    Args:
        code: Authorization code from TrueLayer
        state: State parameter for security (optional)
    
    Returns:
        dict: Message with code for frontend
    """
    return {
        "message": "Authorization successful. Authorization code received.",
        "code": code,
        "state": state,
        "next_step": "POST to /api/truelayer/link-bank with user_id and code"
    }
