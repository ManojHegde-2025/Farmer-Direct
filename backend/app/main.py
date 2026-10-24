"""Rajya Krishi Banda FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.base import engine, Base
from app.api.v1.router import api_router
from app.api.v1.endpoints.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager. Creates tables on startup if not present."""
    # Ensure tables are created in the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup database engine on shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Direct Agricultural Marketplace for Udupi & Dakshina Kannada",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Top-level health check endpoint for monitoring
app.include_router(health_router, tags=["Health"])

# Main API v1 routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "Rajya Krishi Banda API",
        "description": "Full-Stack Agricultural Marketplace for Udupi & Dakshina Kannada",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
    }
