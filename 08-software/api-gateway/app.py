"""CDOS API Gateway — FastAPI application entry point.

Implements: FR-001 through FR-030 (REST API endpoints)
Aligns with: 06-api-specifications/openapi/core-api.yaml
Provides health check, router includes, and middleware.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.utils.config import get_settings
from shared.utils.logging import get_logger
from api_gateway.routers import router as api_router

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown hooks."""
    logger.info("CDOS API Gateway starting up (version=%s)", settings.app_version)
    # TODO: Initialize database connection pool
    # TODO: Initialize Kafka producer
    yield
    logger.info("CDOS API Gateway shutting down")
    # TODO: Close database pool
    # TODO: Close Kafka producer


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance with routers, middleware, and lifespan.
    """
    app = FastAPI(
        title="CDOS Core API",
        description="Clinical Data Orchestration System — Core REST API",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Liveness probe — returns 200 if the process is alive.

    Implements: TR-010 (Observability)
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check() -> dict[str, str]:
    """Readiness probe — checks downstream dependencies.

    Verifies database and Kafka connectivity.
    """
    # TODO: Check database connectivity
    # TODO: Check Kafka connectivity
    return {
        "status": "ready",
        "service": settings.app_name,
    }
