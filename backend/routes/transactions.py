from fastapi import APIRouter, Request, HTTPException
from services.stripe import get_recent_transactions

router = APIRouter()

@router.get("/api/transactions")
async def get_transactions(request: Request):
    """
    Returns the latest 10 transactions for the current user.
    Includes Stripe Radar risk level for each.
    """
    customer_id = request.session.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(status_code=401, detail="No user session found")

    try:
        transactions = get_recent_transactions(customer_id, limit=10)
        return {
            "success": True,
            "count": len(transactions),
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transactions: {str(e)}")