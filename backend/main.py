from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

from routes.user import router as user_router
from routes.webhooks import router as webhooks_router
from routes.carer import router as carer_router
from routes.payments import router as payments_router
from routes.issuing import router as issuing_router
from routes.transactions import router as transactions_router
from routes import truelayer

load_dotenv()

# --- FastAPI app ---
app = FastAPI(title="Alma API", version="1.0.0")

# --- Session middleware ---
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "alma-dev-secret-change-in-prod")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

# --- CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include routers ---
app.include_router(user_router)
app.include_router(truelayer.router)
app.include_router(webhooks_router)
app.include_router(carer_router)
app.include_router(payments_router)
app.include_router(issuing_router)
app.include_router(transactions_router)

# --- Serve static frontend (optional, for production build) ---
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    async def serve_frontend():
        from fastapi.responses import FileResponse
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"status": "Alma API is running", "mode": "test"}
else:
    @app.get("/")
    async def root():
        return {"status": "Alma API is running", "mode": "test"}
