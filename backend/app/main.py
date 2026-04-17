"""FastAPI application factory and configuration."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.bookings import router as bookings_router
from app.audit_logger import AuditLogger
from app.backup import get_backup_manager
from app.database import Base, engine
from app.db_health import check_database_health
from app.environment import validate_environment_on_startup
from app.exceptions import AppException, app_exception_handler, general_exception_handler
from app.feature_flags import get_feature_manager
from app.logger import setup_logging
from app.metrics import get_metrics_collector
from app.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.settings import settings
from app.size_limit_middleware import (
    RequestSizeLimitMiddleware,
    ResponseHeaderValidationMiddleware,
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Application version
__version__ = "1.1.3"
__title__ = "Bus Ticket Booking System API"
__description__ = "Production-ready API for bus ticket booking management with conductor workflow support"

WEBAPP_DIR = Path(__file__).resolve().parents[2] / "webapp"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting application...")
    
    # Validate environment
    if not validate_environment_on_startup():
        logger.error("Environment validation failed - critical errors detected")
        raise RuntimeError("Environment validation failed")
    
    # Log startup event
    AuditLogger.log_system_startup(environment=settings.ENVIRONMENT, version=__version__)
    
    # Initialize database
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    logger.info(f"✓ Application started successfully (v{__version__})")
    
    yield
    
    logger.info("Shutting down application...")
    logger.info("✓ Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    description=__description__,
    summary="Booking and boarding APIs for the bus conductor workflow.",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.ENABLE_SWAGGER_UI else None,
    redoc_url="/api/redoc" if settings.ENABLE_REDOC else None,
    openapi_tags=[
        {
            "name": "Bookings",
            "description": "Booking management and operations",
        },
        {
            "name": "System",
            "description": "System health and status endpoints",
        },
    ],
)

# Add middleware for security and logging (order matters - added in reverse)
# Request validation middleware (innermost - processes first)
app.add_middleware(ResponseHeaderValidationMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
# Security and logging middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
# Response compression middleware (outermost - processes last)
app.add_middleware(GZIPMiddleware, minimum_size=1000)  # Compress responses > 1KB

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


@app.get("/api/health", tags=["System"])
async def health_check() -> dict:
    """Health check endpoint with version information."""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "version": __version__,
        "environment": settings.ENVIRONMENT,
        "api_title": __title__,
    }


@app.get("/", tags=["System"])
async def root() -> dict:
    """Root endpoint with API metadata."""
    return {
        "name": settings.APP_NAME,
        "version": __version__,
        "description": __description__,
        "docs": "/api/docs",
        "status": "active",
    }


@app.get("/api/info", tags=["System"])
async def api_info() -> dict:
    """Get detailed API information."""
    return {
        "title": __title__,
        "version": __version__,
        "description": __description__,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "api_key_enabled": settings.API_KEY_ENABLED,
    }


@app.get("/api/health-detailed", tags=["System"])
async def health_check_detailed() -> dict:
    """Get detailed health check with database and metrics."""
    db_health = check_database_health()
    metrics = get_metrics_collector().get_summary()
    
    return {
        "status": "healthy",
        "version": __version__,
        "environment": settings.ENVIRONMENT,
        "database": db_health,
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/metrics", tags=["System"])
async def get_metrics() -> dict:
    """Get application metrics."""
    collector = get_metrics_collector()
    return {
        "summary": collector.get_summary(),
        "recent_metrics": collector.get_recent_metrics(limit=50),
    }


@app.get("/api/features", tags=["System"])
async def get_features() -> dict:
    """Get feature flags status."""
    manager = get_feature_manager()
    return {
        "features": manager.get_all_features(),
    }


@app.get("/api/backups", tags=["System"])
async def list_backups() -> dict:
    """List available backups."""
    backup_mgr = get_backup_manager()
    backups = backup_mgr.list_backups()
    
    return {
        "backups": backups,
        "total_count": len(backups),
    }


@app.post("/api/backup/create", tags=["System"])
async def create_backup() -> dict:
    """Create a new backup."""
    backup_mgr = get_backup_manager()
    result = backup_mgr.create_backup()
    
    if result["success"]:
        logger.info(f"Backup created: {result['backup_name']}")
    else:
        logger.error(f"Backup creation failed: {result['error']}")
    
    return result


# Mount static files (if they exist)
if WEBAPP_DIR.exists():
    logger.info(f"Mounting static files from {WEBAPP_DIR}")
    app.mount("/", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")
else:
    logger.warning(f"Static files directory not found: {WEBAPP_DIR}")

