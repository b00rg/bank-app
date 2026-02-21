import csv
import os
from datetime import datetime
from typing import Optional, Dict, List

# CSV file path
TRANSACTIONS_CSV = "transactions_data.csv"
CSV_HEADERS = [
    "transaction_id",
    "user_id",
    "type",
    "amount",
    "currency",
    "from_account_id",
    "to_account_id",
    "description",
    "status",
    "created_at"
]


def _ensure_csv_exists():
    """Create CSV file if it doesn't exist."""
    if not os.path.exists(TRANSACTIONS_CSV):
        with open(TRANSACTIONS_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def record_transaction(
    user_id: str,
    transaction_type: str,
    amount: float,
    currency: str,
    from_account_id: str = "",
    to_account_id: str = "",
    description: str = "",
    status: str = "PENDING"
) -> Dict:
    """
    Record a transaction (transfer, payment, etc).
    
    Args:
        user_id: User's unique identifier
        transaction_type: Type of transaction (TRANSFER, PAYMENT, etc)
        amount: Transaction amount
        currency: Currency code
        from_account_id: Source account ID
        to_account_id: Destination account/beneficiary
        description: Transaction description
        status: Transaction status (PENDING, COMPLETED, FAILED)
    
    Returns:
        dict: Transaction data that was saved
    """
    _ensure_csv_exists()
    
    now = datetime.now().isoformat()
    transaction_id = f"txn_{int(datetime.now().timestamp() * 1000)}"
    
    transaction_data = {
        "transaction_id": transaction_id,
        "user_id": user_id,
        "type": transaction_type,
        "amount": amount,
        "currency": currency,
        "from_account_id": from_account_id,
        "to_account_id": to_account_id,
        "description": description,
        "status": status,
        "created_at": now
    }
    
    # Append to CSV
    with open(TRANSACTIONS_CSV, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(transaction_data)
    
    return transaction_data


def get_user_transactions(user_id: str, limit: int = 50) -> List[Dict]:
    """
    Get all transactions for a specific user.
    
    Args:
        user_id: User's unique identifier
        limit: Maximum number of transactions to return
    
    Returns:
        list: List of transaction dictionaries
    """
    _ensure_csv_exists()
    
    transactions = []
    if os.path.exists(TRANSACTIONS_CSV):
        with open(TRANSACTIONS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["user_id"] == user_id:
                    transactions.append(row)
    
    # Return latest first
    return sorted(transactions, key=lambda x: x.get("created_at"), reverse=True)[:limit]


def get_all_transactions(limit: int = 100) -> List[Dict]:
    """
    Get all transactions.
    
    Args:
        limit: Maximum number of transactions to return
    
    Returns:
        list: List of all transaction dictionaries
    """
    _ensure_csv_exists()
    
    transactions = []
    if os.path.exists(TRANSACTIONS_CSV):
        with open(TRANSACTIONS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            transactions = list(reader)
    
    # Return latest first
    return sorted(transactions, key=lambda x: x.get("created_at"), reverse=True)[:limit]


def update_transaction_status(transaction_id: str, status: str) -> bool:
    """
    Update the status of a transaction.
    
    Args:
        transaction_id: Transaction ID to update
        status: New status (COMPLETED, FAILED, CANCELLED, etc)
    
    Returns:
        bool: True if updated, False if not found
    """
    _ensure_csv_exists()
    
    transactions = []
    found = False
    
    if os.path.exists(TRANSACTIONS_CSV):
        with open(TRANSACTIONS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["transaction_id"] == transaction_id:
                    row["status"] = status
                    found = True
                transactions.append(row)
    
    # Write back to CSV
    with open(TRANSACTIONS_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(transactions)
    
    return found
