import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

from api.errors import register_exception_handlers
from api.middleware import register_middlewares
from api.router import API_V1_PREFIX, api_router
from core.config import AppConfig, AuthConfig, LoggingConfig, TelemetryConfig
from core.logging import setup_logging
from core.telemetry import setup_telemetry
from infra.dependencies import container

logger = logging.getLogger("api.main")


def create_app() -> FastAPI:
    app_config = AppConfig()
    telemetry = setup_telemetry(
        service_name="booking-api",
        service_version=app_config.APP_VERSION,
        config=TelemetryConfig(),
    )
    setup_logging(LoggingConfig(), telemetry.logging_handler)
    auth_config = AuthConfig()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            try:
                await container.close()
            finally:
                logger.info("application_shutdown_finished")
                telemetry.shutdown()

    app = FastAPI(
        title="Booking meeting rooms API",
        version=app_config.APP_VERSION,
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

    if telemetry.tracer_provider is not None:
        RedisInstrumentor().instrument(
            tracer_provider=telemetry.tracer_provider,
        )
    if (
        telemetry.tracer_provider is not None
        or telemetry.meter_provider is not None
    ):
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=telemetry.tracer_provider,
            meter_provider=telemetry.meter_provider,
            excluded_urls="healthcheck",
            exclude_spans=["receive", "send"],
        )

    logger.info("application_initialized title=%s", app.title)
    return app


app = create_app()
