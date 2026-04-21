"""FastAPI application factory and configuration."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.bookings import router as bookings_router
from app.api_docs import get_doc_generator
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
from app.migrations import get_migration_manager
from app.profiler import get_profiler
from app.security_scanner import SecurityScanner
from app.settings import settings
from app.size_limit_middleware import (
    RequestSizeLimitMiddleware,
    ResponseHeaderValidationMiddleware,
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Application version
__version__ = "1.1.5"
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
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB

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
    # logger.debug("Health check requested")  # Removed for production cleanliness
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


@app.get("/api/profiling/stats", tags=["System"])
async def get_profiling_stats() -> dict:
    """Get application profiling statistics."""
    profiler = get_profiler()
    stats = profiler.get_statistics()
    slowest = profiler.get_slowest_operations(limit=10)
    
    return {
        "statistics": stats,
        "slowest_operations": slowest,
    }


@app.get("/api/migrations/status", tags=["System"])
async def get_migrations_status() -> dict:
    """Get database migration status."""
    manager = get_migration_manager()
    status = manager.get_status()
    
    return {
        "migrations": status,
    }


@app.post("/api/migrations/apply", tags=["System"])
async def apply_migrations() -> dict:
    """Apply pending database migrations."""
    from app.migrations import apply_pending_migrations
    
    result = apply_pending_migrations()
    logger.info(f"Migrations applied: {result['applied_migrations']}")
    return result


@app.post("/api/security/scan", tags=["System"])
async def run_security_scan() -> dict:
    """Run security scan on system configuration."""
    scanner = SecurityScanner()
    result = scanner.scan_configuration(settings.dict())
    
    return {
        "scan_result": result.to_dict(),
    }


@app.get("/api/docs/markdown", tags=["System"])
async def get_api_docs_markdown() -> dict:
    """Get API documentation in Markdown format."""
    doc_gen = get_doc_generator()
    
    # Register default endpoints
    doc_gen.register_endpoint(
        method="GET",
        path="/api/bookings",
        summary="List all bookings",
        description="Retrieve a paginated list of bookings",
        tags=["Bookings"],
        response_schema={"bookings": [], "total": 0},
        example_response={"bookings": [], "total": 0},
    )
    
    return {
        "documentation": doc_gen.get_markdown_doc(),
    }


@app.get("/api/docs/openapi", tags=["System"])
async def get_api_docs_openapi() -> dict:
    """Get API documentation in OpenAPI 3.0 format."""
    doc_gen = get_doc_generator()
    return doc_gen.get_openapi_schema()


# Mount static files (if they exist)
if WEBAPP_DIR.exists():
    logger.info(f"Mounting static files from {WEBAPP_DIR}")
    app.mount("/", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")
else:
    logger.warning(f"Static files directory not found: {WEBAPP_DIR}")

