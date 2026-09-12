import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import health, products, forecasts, risk, dashboard, alerts

# Windows consoles default to cp1252, which cannot encode some log characters.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable stream
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    print("Starting PriceShock API...")
    init_db()
    print("Database initialized")
    print("API Documentation: http://localhost:8000/docs")
    yield


# Initialize FastAPI app
app = FastAPI(
    title="PriceShock API",
    description="Product Price Forecasting & Inflation Early-Warning System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
# In production, set CORS_ORIGINS to a comma-separated list of allowed
# frontend origins (e.g. "https://myapp.onrender.com"). Defaults to the
# local dev origins so the app keeps working out of the box.
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
_cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (each router declares its own full /api/... paths)
app.include_router(health.router, tags=["health"])
app.include_router(products.router, tags=["products"])
app.include_router(forecasts.router, tags=["forecasts"])
app.include_router(risk.router, tags=["risk"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(alerts.router, tags=["alerts"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PriceShock API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/api/health",
    }