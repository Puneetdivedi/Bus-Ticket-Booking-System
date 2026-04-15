"""FastAPI application factory and configuration."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.bookings import router as bookings_router
from app.database import Base, engine
from app.exceptions import AppException, app_exception_handler, general_exception_handler
from app.logger import setup_logging
from app.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.settings import settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

WEBAPP_DIR = Path(__file__).resolve().parents[2] / "webapp"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting application...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    summary="Booking and boarding APIs for the bus conductor workflow.",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.ENABLE_SWAGGER_UI else None,
    redoc_url="/api/redoc" if settings.ENABLE_REDOC else None,
)

# Add middleware for security and logging
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(bookings_router)


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }


# Mount static files (if they exist)
if WEBAPP_DIR.exists():
    logger.info(f"Mounting static files from {WEBAPP_DIR}")
    app.mount("/", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")
else:
    logger.warning(f"Static files directory not found: {WEBAPP_DIR}")

