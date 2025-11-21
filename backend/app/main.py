# backend/app/main.py
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   # ⭐ NEW — serve screenshots

# Routers
from .routers import scan, reports

# Database init
from .database import init_db

# -----------------------------
# FastAPI App Initialization
# -----------------------------
app = FastAPI(
    title="Inclusive Web Validator API",
    version="1.0.0",
    description="Backend API for automated accessibility compliance scanning."
)

# ⭐ Serve screenshots and report assets
# Anything inside reports_output/ becomes accessible at: /static/*
app.mount("/static", StaticFiles(directory="reports_output"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(scan.router)
app.include_router(reports.router)

# -----------------------------
# Startup Event
# -----------------------------
@app.on_event("startup")
async def on_startup():
    init_db()

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "Inclusive Web Validator backend is running"}
