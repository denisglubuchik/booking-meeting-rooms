import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors import register_exception_handlers
from api.middleware import register_middlewares
from api.router import API_V1_PREFIX, api_router
from core.config import AuthConfig, LoggingConfig
from core.logging import setup_logging
from infra.dependencies import container

setup_logging(LoggingConfig())
logger = logging.getLogger("api.main")
auth_config = AuthConfig()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await container.close()
    logger.info("application_shutdown_finished")


app = FastAPI(
    title="Booking meeting rooms API",
    version="1.0.0",
    docs_url=f"{API_V1_PREFIX}/docs",
    redoc_url=f"{API_V1_PREFIX}/redoc",
    openapi_url=f"{API_V1_PREFIX}/openapi.json",
    swagger_ui_oauth2_redirect_url=(
        f"{API_V1_PREFIX}/docs/oauth2-redirect"
    ),
    lifespan=lifespan,
)
register_exception_handlers(app)
register_middlewares(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in auth_config.CORS_ALLOW_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck", status_code=200, tags=["General"])
def check_service_health() -> None:
    return


app.include_router(api_router)


setup_dishka(container, app)
logger.info("application_initialized title=%s", app.title)
