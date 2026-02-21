import csv
import os
from datetime import datetime
from typing import Optional, Dict, List

# CSV file path
USERS_CSV = "users_data.csv"
CSV_HEADERS = [
    "user_id",
    "name",
    "email",
    "phone",
    "access_token",
    "token_type",
    "expires_in",
    "primary_account_id",
    "primary_account_name",
    "created_at",
    "updated_at"
]


def _ensure_csv_exists():
    """Create CSV file if it doesn't exist."""
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def save_user(
    user_id: str,
    name: str,
    email: str,
    phone: str = "",
    access_token: str = "",
    token_type: str = "",
    expires_in: int = 0,
    primary_account_id: str = "",
    primary_account_name: str = ""
) -> Dict:
    """
    Save or update user data to CSV.
    
    Args:
        user_id: Unique user identifier
        name: User's full name
        email: User's email
        phone: User's phone number
        access_token: TrueLayer access token
        token_type: Token type (Bearer)
        expires_in: Token expiration in seconds
        primary_account_id: User's primary bank account ID
        primary_account_name: User's primary bank account name
    
    Returns:
        dict: User data that was saved
    """
    _ensure_csv_exists()
    
    now = datetime.now().isoformat()
    user_data = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "access_token": access_token,
        "token_type": token_type,
        "expires_in": expires_in,
        "primary_account_id": primary_account_id,
        "primary_account_name": primary_account_name,
        "created_at": "",
        "updated_at": now
    }
    
    # Read existing users
    users = []
    user_exists = False
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["user_id"] == user_id:
                    user_exists = True
                    # Update existing user
                    row.update(user_data)
                    row["created_at"] = row.get("created_at", now)
                    row["updated_at"] = now
                    users.append(row)
                else:
                    users.append(row)
    
    # Add new user if not exists
    if not user_exists:
        user_data["created_at"] = now
        users.append(user_data)
    
    # Write back to CSV
    with open(USERS_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(users)
    
    return user_data


def get_user(user_id: str) -> Optional[Dict]:
    """
    Retrieve user data from CSV.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        dict: User data or None if not found
    """
    _ensure_csv_exists()
    
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["user_id"] == user_id:
                    return row
    return None


def get_all_users() -> List[Dict]:
    """
    Retrieve all users from CSV.
    
    Returns:
        list: List of all user dictionaries
    """
    _ensure_csv_exists()
    
    users = []
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            users = list(reader)
    return users


def delete_user(user_id: str) -> bool:
    """
    Delete a user from CSV.
    
    Args:
        user_id: User's unique identifier
    
    Returns:
        bool: True if user was deleted, False if not found
    """
    _ensure_csv_exists()
    
    users = []
    found = False
    
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["user_id"] != user_id:
                    users.append(row)
                else:
                    found = True
    
    # Write back to CSV
    with open(USERS_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(users)
    
    return found


def user_exists(user_id: str) -> bool:
    """Check if user exists in CSV."""
    return get_user(user_id) is not None
