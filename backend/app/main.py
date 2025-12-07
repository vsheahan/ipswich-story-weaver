"""Main FastAPI application for Neighborhood Story Weaver."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize database tables (in production, use migrations instead)
    if settings.debug:
        await init_db()
        logger.info("Database tables initialized")

    yield

    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Neighborhood Story Weaver generates daily fictionalized stories about
    Ipswich, Massachusetts, weaving together weather data, tidal patterns,
    seasonal rhythms, and community-submitted anecdotes into an evolving
    narrative about this historic coastal town.
    """,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/healthz")
async def healthz():
    """
    Lightweight health check endpoint for App Runner.

    Returns a simple status check. For production, you may want to add
    database connectivity checks, but keep this fast for frequent polling.
    """
    return {"status": "ok"}


@app.get("/healthz/ready")
async def readiness_check():
    """
    Readiness check that verifies database connectivity.

    Use this for more thorough health checks that include dependencies.
    """
    from app.core.database import async_session_maker
    from sqlalchemy import text

    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Daily stories woven from the fabric of Ipswich, MA",
        "docs_url": "/docs",
        "api_prefix": "/api",
    }
