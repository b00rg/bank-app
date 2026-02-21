import requests
import os
import json
import uuid
import hmac
import hashlib
import base64
from dotenv import load_dotenv

load_dotenv()

# Environment variables
TRUELAYER_CLIENT_ID = os.getenv("TRUELAYER_CLIENT_ID")
TRUELAYER_CLIENT_SECRET = os.getenv("TRUELAYER_CLIENT_SECRET")
TRUELAYER_REDIRECT_URI = os.getenv("TRUELAYER_REDIRECT_URI")

# TrueLayer API URLs (official)
TRUELAYER_AUTH_URL = "https://auth.truelayer.com"
TRUELAYER_API_URL = "https://api.truelayer.com"


def get_authorization_url() -> str:
    """
    Generates the OAuth authorization URL for user to link their bank.
    User should be redirected to this URL.
    
    Returns:
        str: OAuth authorization URL
    """
    auth_url = (
        f"{TRUELAYER_AUTH_URL}/?"
        f"client_id={TRUELAYER_CLIENT_ID}&"
        f"redirect_uri={TRUELAYER_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=info%20accounts%20transactions%20balance%20offline_access&"
        f"providers=ie-ob-all"
    )
    return auth_url


def exchange_code_for_token(auth_code: str) -> dict:
    """
    Exchanges authorization code for access token.
    Called after user approves bank access.
    
    Args:
        auth_code (str): Authorization code from TrueLayer OAuth callback
    
    Returns:
        dict: Response with access_token, token_type, expires_in
    """
    url = f"{TRUELAYER_AUTH_URL}/connect/token"
    
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": TRUELAYER_CLIENT_ID,
        "client_secret": TRUELAYER_CLIENT_SECRET,
        "redirect_uri": TRUELAYER_REDIRECT_URI
    }
    
    print(f"[DEBUG] Token exchange URL: {url}")
    print(f"[DEBUG] Request data: {data}")
    
    try:
        response = requests.post(url, data=data, timeout=10)
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response body: {response.text}")
        
        if response.status_code != 200:
            return {
                "error": f"Token endpoint returned {response.status_code}",
                "status_code": response.status_code,
                "response_body": response.text
            }
        
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Request failed: {str(e)}",
            "details": str(e)
        }
    except Exception as e:
        return {
            "error": f"Token exchange failed: {str(e)}",
            "details": str(e)
        }


def get_payments_token() -> dict:
    """
    Gets a payments access token using client credentials flow.
    Required for initiating payments via TrueLayer Payments API.
    
    This uses the grant_type=client_credentials with the 'payments' scope.
    
    Returns:
        dict: Response with access_token, token_type, expires_in
    """
    url = f"{TRUELAYER_AUTH_URL}/connect/token"
    
    data = {
        "grant_type": "client_credentials",
        "client_id": TRUELAYER_CLIENT_ID,
        "client_secret": TRUELAYER_CLIENT_SECRET,
        "scope": "payments"
    }
    
    print(f"[DEBUG] Payments token exchange URL: {url}")
    print(f"[DEBUG] Request scope: payments")
    
    try:
        response = requests.post(url, data=data, timeout=10)
        print(f"[DEBUG] Payments token response status: {response.status_code}")
        print(f"[DEBUG] Payments token response body: {response.text}")
        
        if response.status_code != 200:
            return {
                "error": f"Payments token endpoint returned {response.status_code}",
                "status_code": response.status_code,
                "response_body": response.text
            }
        
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Payments token request failed: {str(e)}",
            "details": str(e)
        }
    except Exception as e:
        return {
            "error": f"Payments token exchange failed: {str(e)}",
            "details": str(e)
        }


def create_payment_signature(request_body: dict) -> str:
    """
    Creates a JWS signature for Payments API requests.
    TrueLayer requires signed payment requests for security.
    
    Args:
        request_body (dict): The payment request body to sign
    
    Returns:
        str: Base64-encoded JWS signature
    """
    # Serialize the request body to JSON
    body_string = json.dumps(request_body, separators=(',', ':'), sort_keys=True)
    
    # Create the signature using HMAC-SHA256
    signature = hmac.new(
        TRUELAYER_CLIENT_SECRET.encode(),
        body_string.encode(),
        hashlib.sha256
    ).digest()
    
    # Base64 encode the signature
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    
    print(f"[DEBUG] Created payment signature for request body")
    
    return signature_b64


def link_user_bank(user_id: str, auth_code: str) -> dict:
    """
    Links a user's bank account via TrueLayer OAuth.
    This initializes the user for banking operations.
    
    Args:
        user_id (str): Your application's user ID
        auth_code (str): Authorization code from TrueLayer callback
    
    Returns:
        dict: Contains user_id, access_token, token_type, expires_in, and accounts
    """
    # Exchange auth code for access token
    token_response = exchange_code_for_token(auth_code)
    
    if "error" in token_response or "access_token" not in token_response:
        return {
            "error": "Failed to get access token",
            "details": token_response
        }
    
    access_token = token_response.get("access_token")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        url = f"{TRUELAYER_API_URL}/data/v1/accounts"
        accounts_response = requests.get(url, headers=headers)
        accounts_response.raise_for_status()
        
        return {
            "user_id": user_id,
            "access_token": access_token,
            "token_type": token_response.get("token_type"),
            "expires_in": token_response.get("expires_in"),
            "accounts": accounts_response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Failed to fetch accounts: {str(e)}",
            "access_token": access_token  # Still return token even if accounts fetch fails
        }


def get_accounts(access_token: str = None) -> dict:
    """
    Fetches user's bank accounts via TrueLayer.
    
    Args:
        access_token (str): User's access token (uses env var if not provided)
    
    Returns:
        dict: Response with list of accounts
    """
    token = access_token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"{TRUELAYER_API_URL}/data/v1/accounts"
    response = requests.get(url, headers=headers)
    return response.json()


def get_transactions(account_id: str, access_token: str = None) -> dict:
    """
    Fetches transactions for a given account.
    
    Args:
        account_id (str): The account ID
        access_token (str): User's access token (uses env var if not provided)
    
    Returns:
        dict: Response with list of transactions
    """
    token = access_token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{TRUELAYER_API_URL}/data/v1/accounts/{account_id}/transactions"
    response = requests.get(url, headers=headers)
    return response.json()


def get_balance(account_id: str, access_token: str = None) -> dict:
    """
    Fetches balance for a given account.
    
    Args:
        account_id (str): The account ID
        access_token (str): User's access token (uses env var if not provided)
    
    Returns:
        dict: Response with account balance info
    """
    token = access_token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{TRUELAYER_API_URL}/data/v1/accounts/{account_id}/balance"
    response = requests.get(url, headers=headers)
    return response.json()


def initiate_transfer(
    amount: float,
    currency: str,
    from_account_id: str,
    to_account_id: str,
    reference: str = "",
    access_token: str = None
) -> dict:
    """
    Initiates a transfer between accounts (same user or different users).
    
    Args:
        amount (float): Transfer amount
        currency (str): Currency code (GBP, EUR, USD, etc.)
        from_account_id (str): Source account ID
        to_account_id (str): Destination account ID
        reference (str): Transfer reference/description
        access_token (str): User's access token
    
    Returns:
        dict: Response with transfer confirmation and status
    """
    token = access_token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{TRUELAYER_API_URL}/transfers"
    data = {
        "amount": amount,
        "currency": currency,
        "from_account_id": from_account_id,
        "to_account_id": to_account_id,
        "reference": reference
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def initiate_payment(
    amount: float,
    currency: str,
    beneficiary_name: str,
    beneficiary_account: str,
    from_account_id: str = None
) -> dict:
    """
    Initiates a payment via TrueLayer Payments API.
    
    Uses client credentials token (not user token) for payment initiation.
    The payment will be debited from the user's linked account.
    
    Args:
        amount (float): Payment amount
        currency (str): Currency code (GBP, EUR, USD, etc.)
        beneficiary_name (str): Recipient name
        beneficiary_account (str): Recipient bank account/IBAN
        from_account_id (str): Optional source account ID
    
    Returns:
        dict: Response with payment confirmation and status
    """
    # Get payments token using client credentials
    token_response = get_payments_token()
    
    if "error" in token_response or "access_token" not in token_response:
        return {
            "error": "Failed to obtain payments token",
            "details": token_response.get("error", "Unknown error"),
            "response": token_response
        }
    
    payments_token = token_response["access_token"]
    
    # Create the payment request body
    data = {
        "amount": amount,
        "currency": currency,
        "beneficiary": {
            "name": beneficiary_name,
            "account_identifier": {
                "type": "iban",
                "iban": beneficiary_account
            }
        }
    }
    
    if from_account_id:
        data["from_account_id"] = from_account_id
    
    # Create signature and idempotency key (required by TrueLayer)
    signature = create_payment_signature(data)
    idempotency_key = str(uuid.uuid4())
    
    headers = {
        "Authorization": f"Bearer {payments_token}",
        "Content-Type": "application/json",
        "Tl-Signature": signature,
        "Idempotency-Key": idempotency_key
    }
    url = f"{TRUELAYER_API_URL}/payments"
    
    print(f"[DEBUG] Initiating payment: {amount} {currency} to {beneficiary_name}")
    print(f"[DEBUG] Idempotency-Key: {idempotency_key}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"[DEBUG] Payment response status: {response.status_code}")
        print(f"[DEBUG] Payment response: {response.text}")
        
        if response.status_code not in [200, 201, 202]:
            return {
                "error": "Payment initiation failed",
                "status_code": response.status_code,
                "response": response.json() if response.text else {}
            }
        
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Payment request failed: {str(e)}",
            "details": str(e)
        }
    except Exception as e:
        return {
            "error": f"Payment initiation failed: {str(e)}",
            "details": str(e)
        }
