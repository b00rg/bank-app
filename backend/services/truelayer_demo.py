import requests
import os
from dotenv import load_dotenv

load_dotenv()

TRUELAYER_CLIENT_ID = os.getenv("TRUELAYER_CLIENT_ID")
TRUELAYER_CLIENT_SECRET = os.getenv("TRUELAYER_CLIENT_SECRET")
TRUELAYER_REDIRECT_URI = os.getenv("TRUELAYER_REDIRECT_URI")
TRUELAYER_ACCESS_TOKEN = os.getenv("TRUELAYER_ACCESS_TOKEN")
TRUELAYER_API_URL = "https://api.truelayer.com"


def get_authorization_url():
    """
    Generates the OAuth authorization URL for user to link their bank.
    User should be redirected to this URL.
    """
    auth_url = (
        f"https://auth.truelayer.com/authorize?"
        f"client_id={TRUELAYER_CLIENT_ID}&"
        f"redirect_uri={TRUELAYER_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=accounts%20transactions%20balance%20payments"
    )
    return auth_url


def exchange_code_for_token(auth_code: str) -> dict:
    """
    Exchanges authorization code for access token.
    Called after user approves bank access.
    Returns dict with access_token and expiry info.
    """
    url = "https://auth.truelayer.com/connect/token"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": TRUELAYER_CLIENT_ID,
        "client_secret": TRUELAYER_CLIENT_SECRET,
        "redirect_uri": TRUELAYER_REDIRECT_URI
    }
    response = requests.post(url, data=data)
    return response.json()


def link_user_bank(user_id: str, auth_code: str) -> dict:
    """
    Links a user's bank account via TrueLayer OAuth.
    This initializes the user for banking operations.
    Stores the access token for future API calls.
    """
    # Exchange auth code for access token
    token_response = exchange_code_for_token(auth_code)
    
    if "access_token" not in token_response:
        return {"error": "Failed to get access token", "details": token_response}
    
    access_token = token_response.get("access_token")
    
    # Fetch user's accounts to verify connection
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{TRUELAYER_API_URL}/data/v1/accounts"
    accounts_response = requests.get(url, headers=headers)
    
    # Return success with stored token and user accounts
    return {
        "user_id": user_id,
        "access_token": access_token,
        "token_type": token_response.get("token_type"),
        "expires_in": token_response.get("expires_in"),
        "accounts": accounts_response.json()
    }


def get_accounts():
    """Fetches user's bank accounts via TrueLayer."""
    headers = {
        "Authorization": f"Bearer {TRUELAYER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"{TRUELAYER_API_URL}/data/v1/accounts"
    response = requests.get(url, headers=headers)
    return response.json()


def get_transactions(account_id):
    """Fetches transactions for a given account."""
    headers = {
        "Authorization": f"Bearer {TRUELAYER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"{TRUELAYER_API_URL}/data/v1/accounts/{account_id}/transactions"
    response = requests.get(url, headers=headers)
    return response.json()


def get_balance(account_id):
    """Fetches balance for a given account."""
    headers = {
        "Authorization": f"Bearer {TRUELAYER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"{TRUELAYER_API_URL}/data/v1/accounts/{account_id}/balance"
    response = requests.get(url, headers=headers)
    return response.json()


def initiate_payment(amount, currency, beneficiary_name, beneficiary_account):
    """Initiates a payment via TrueLayer (simplified)."""
    headers = {
        "Authorization": f"Bearer {TRUELAYER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"{TRUELAYER_API_URL}/payments"
    data = {
        "amount": amount,
        "currency": currency,
        "beneficiary_name": beneficiary_name,
        "beneficiary_account": beneficiary_account
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
