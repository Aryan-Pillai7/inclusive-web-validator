# backend/app/main.py
# backend/app/main.py
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers (to be created in later steps)
from .routers import scan, reports

# Database init (to be created in Step 2)
from .database import init_db

# -----------------------------
# FastAPI App Initialization
# -----------------------------
app = FastAPI(
    title="Inclusive Web Validator API",
    version="1.0.0",
    description="Backend API for automated accessibility compliance scanning."
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers (will exist after steps 5 and 6)
app.include_router(scan.router)
app.include_router(reports.router)

# -----------------------------
# Startup Event
# -----------------------------
@app.on_event("startup")
async def on_startup():
    """Initialize database connection at startup."""
    init_db()

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "Inclusive Web Validator backend is running"}
