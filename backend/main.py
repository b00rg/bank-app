from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

from backend.routes.user import router as user_router
# from backend.routes.chat import router as chat_router         # add when ready
# from backend.routes.speak import router as speak_router       # add when ready
# from backend.routes.transactions import router as transactions_router
# from backend.routes.payments import router as payments_router
from backend.routes import truelayer
from routes.user import router as user_router
from routes.webhooks import router as webhooks_router
from routes.carer import router as carer_router
from routes.payments import router as payments_router
from routes.issuing import router as issuing_router

load_dotenv()

app = FastAPI(title="Alma API", version="1.0.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "alma-dev-secret-change-in-prod")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(truelayer.router)
app.include_router(webhooks_router)
app.include_router(carer_router)
app.include_router(payments_router)
app.include_router(issuing_router)
app.include_router(transactions_router)
# app.include_router(chat_router)
# app.include_router(speak_router)

# --- Static Files ---
# Serve index.html and other static files
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# app.include_router(chat_router)
# app.include_router(speak_router)

# --- Health check ---

@app.get("/")
async def root():
    return {"status": "Alma API is running", "mode": "test"}