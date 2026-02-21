from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

from routes.user import router as user_router
from routes.webhooks import router as webhooks_router
from routes.carer import router as carer_router
from routes.payments import router as payments_router
from routes.transactions import router as transactions_router
# from routes.chat import router as chat_router         # add when ready
# from routes.speak import router as speak_router       # add when ready

load_dotenv()

app = FastAPI(title="Alma API", version="1.0.0")

# --- Middleware ---

# Session middleware (stores session data server-side via signed cookie)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "alma-dev-secret-change-in-prod")
)

# CORS — allows React frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # Required for session cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---

app.include_router(user_router)
app.include_router(webhooks_router)
app.include_router(carer_router)
app.include_router(payments_router)
app.include_router(transactions_router)
# app.include_router(chat_router)
# app.include_router(speak_router)


# --- Health check ---

@app.get("/")
async def root():
    return {"status": "Alma API is running", "mode": "test"}