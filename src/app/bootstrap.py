"""
Application Bootstrap - Assembly and Configuration.
Creates and configures the FastAPI application with all middleware,
routers, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.app.config.settings import settings
from src.app.db.session import engine
from src.app.db.base import Base


def configure_logging() -> logging.Logger:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO if settings.DEBUG else logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger(__name__)


logger = configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API available at: {settings.API_V1_PREFIX}")

    # Import models module to register all models with Base
    from src.app.db import models  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Auto-seed database if empty
    from seeds.base import auto_seed_if_empty
    auto_seed_if_empty()

    yield

    # Shutdown
    logger.info("Application shutting down")


def create_application() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    _register_routers(application)

    # Register root endpoints
    _register_root_endpoints(application)

    return application


def _register_routers(app: FastAPI) -> None:
    """Register all module routers."""
    from src.app.modules.users.router import router as users_router
    from src.app.modules.quizzes.router import router as quizzes_router
    from src.app.modules.sectors.router import router as sectors_router
    from src.app.modules.goals.router import router as goals_router
    from src.app.modules.admin.router import router as admin_router

    app.include_router(users_router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
    app.include_router(quizzes_router, prefix=f"{settings.API_V1_PREFIX}/quizzes", tags=["Quizzes"])
    app.include_router(sectors_router, prefix=f"{settings.API_V1_PREFIX}/sectors", tags=["Sectors"])
    app.include_router(goals_router, prefix=f"{settings.API_V1_PREFIX}/goals", tags=["Goals"])
    app.include_router(admin_router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])


def _register_root_endpoints(app: FastAPI) -> None:
    """Register root-level endpoints."""

    @app.get("/", tags=["Root"])
    def root():
        """Root endpoint - Welcome message."""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "api": settings.API_V1_PREFIX,
            "docs": "/docs",
            "redoc": "/redoc",
        }

    @app.get("/health", tags=["Health"])
    def health_check():
        """Health check endpoint for container orchestration."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/welcome", tags=["Root"])
    def welcome(request: Request):
        """Welcome endpoint that logs requests and returns a welcome message."""
        logger.info(f"Request received: {request.method} {request.url.path}")
        return {"message": f"Welcome to the {settings.PROJECT_NAME}"}
