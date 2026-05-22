import logging
from time import perf_counter

from fastapi import FastAPI, Request

from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Backend API for the AI financial intelligence platform.",
        version=settings.app_version,
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = perf_counter()
        response = await call_next(request)
        duration_ms = round((perf_counter() - start) * 1000, 2)

        logger.info(
            "request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response

    app.include_router(health_router)

    logger.info(
        "application started",
        extra={
            "environment": settings.app_env,
            "version": settings.app_version,
        },
    )

    return app


app = create_app()
