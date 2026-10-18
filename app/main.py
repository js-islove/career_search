from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.logging import configure_logging, get_logger
from app.core.errors import PlatformError, make_error_envelope


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the application."""
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    configure_logging(level=log_level)
    logger = get_logger("app.main")
    logger.info("application_startup", debug=settings.DEBUG, host=settings.APP_HOST, port=settings.APP_PORT)
    yield
    logger.info("application_shutdown")


app = FastAPI(
    title="Job Aggregation & Matching Platform",
    description="Automated job discovery, ingestion, normalization, and search API.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(PlatformError)
async def platform_error_handler(request: Request, exc: PlatformError):
    """Catches custom platform domain errors and maps them to the standard envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content=make_error_envelope(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catches unhandled unexpected errors, logs them, and returns a safe 500 envelope."""
    logger = get_logger("app.main")
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=make_error_envelope(
            code="internal_error",
            message="An unexpected internal server error occurred.",
        ),
    )


@app.get("/healthz", tags=["Health"])
async def healthz():
    """
    Liveness probe: verifies that the web server process is alive and accepting requests.
    """
    return {"status": "healthy"}


@app.get("/readyz", tags=["Health"])
async def readyz():
    """
    Readiness probe: verifies that critical backing services (PostgreSQL) are operational.
    Returns 200 if connected, 503 if unreachable.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as exc:
        logger = get_logger("app.main")
        logger.error("readiness_check_failed", error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "disconnected",
                "error": "Database connectivity check failed",
            },
        )


@app.get("/", tags=["General"])
async def root():
    """Root endpoint providing service discovery info."""
    return {
        "service": "Job Aggregation & Matching Platform API",
        "version": "0.1.0",
        "status": "online",
        "docs": "/docs",
    }
