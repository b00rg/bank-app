from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.alerts import send_carer_sms, build_registration_message

router = APIRouter()


class RegisterCarerRequest(BaseModel):
    carer_name: str
    carer_phone: str   # e.g. +353871234567


@router.post("/api/carer/register")
async def register_carer(request: Request, body: RegisterCarerRequest):
    """
    Links a carer/trusted contact to the user's session.
    Stores carer name and phone number in session.
    Sends a confirmation SMS to the carer.
    """
    if not request.session.get("stripe_customer_id"):
        raise HTTPException(status_code=401, detail="No user session found. Please complete onboarding first.")

    user_name = request.session.get("user_name", "your loved one")

    # Store carer in session
    request.session["carer_name"] = body.carer_name
    request.session["carer_phone"] = body.carer_phone

    # Send confirmation SMS to carer
    send_carer_sms(
        carer_phone=body.carer_phone,
        message=build_registration_message(user_name)
    )

    return JSONResponse(content={
        "success": True,
        "message": f"{body.carer_name} has been registered as your trusted contact.",
        "carer_phone": body.carer_phone,
        "alma_message": f"I've let {body.carer_name} know they've been added as your trusted contact. They'll get a text if anything looks unusual."
    })


@router.get("/api/carer")
async def get_carer(request: Request):
    """
    Returns the current carer linked to the user's session.
    """
    carer_phone = request.session.get("carer_phone")
    carer_name = request.session.get("carer_name")

    if not carer_phone:
        return JSONResponse(content={"carer": None})

    return JSONResponse(content={
        "carer": {
            "name": carer_name,
            "phone": carer_phone,
        }
    })


@router.delete("/api/carer")
async def remove_carer(request: Request):
    """
    Removes the carer from the user's session.
    """
    request.session.pop("carer_phone", None)
    request.session.pop("carer_name", None)

    return JSONResponse(content={
        "success": True,
        "alma_message": "I've removed your trusted contact."
    })