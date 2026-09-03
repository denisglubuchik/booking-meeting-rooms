from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppConfig(Settings):
    APP_VERSION: str = "1.0.0"


class DBConfig(Settings):
    PG_PORT: int = 5432
    PG_DB: str
    PG_USER: str
    PG_PASS: str
    PG_HOST: str | None = None

    PG_RW_HOST: str | None = None
    PG_RW_PORT: int | None = None
    PG_RW_DB: str | None = None
    PG_RW_USER: str | None = None
    PG_RW_PASS: str | None = None

    PG_RO_HOST: str | None = None
    PG_RO_PORT: int | None = None
    PG_RO_DB: str | None = None
    PG_RO_USER: str | None = None
    PG_RO_PASS: str | None = None

    @staticmethod
    def _url(
        *,
        host: str | None,
        port: int,
        database: str,
        user: str,
        password: str,
    ) -> str:
        if host is None:
            msg = "PG_RW_HOST/PG_RO_HOST or legacy PG_HOST must be set"
            raise ValueError(msg)
        return (
            f"postgresql+asyncpg://{user}:{password}@"
            f"{host}:{port}/{database}"
        )

    @property
    def RW_DATABASE_URL(self) -> str:  # noqa: N802
        return self._url(
            host=self.PG_RW_HOST or self.PG_HOST,
            port=self.PG_RW_PORT or self.PG_PORT,
            database=self.PG_RW_DB or self.PG_DB,
            user=self.PG_RW_USER or self.PG_USER,
            password=self.PG_RW_PASS or self.PG_PASS,
        )

    @property
    def RO_DATABASE_URL(self) -> str:  # noqa: N802
        return self._url(
            host=self.PG_RO_HOST or self.PG_RW_HOST or self.PG_HOST,
            port=self.PG_RO_PORT or self.PG_RW_PORT or self.PG_PORT,
            database=self.PG_RO_DB or self.PG_RW_DB or self.PG_DB,
            user=self.PG_RO_USER or self.PG_RW_USER or self.PG_USER,
            password=self.PG_RO_PASS or self.PG_RW_PASS or self.PG_PASS,
        )

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        """Backward-compatible alias used by Alembic."""
        return self.RW_DATABASE_URL


class RedisConfig(Settings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_USER: str
    REDIS_DB: int
    APP_REDIS_PREFIX: str = "booking:back"


class AuthConfig(Settings):
    JWT_ACCESS_SECRET: str = "change-me-in-env"
    JWT_ACCESS_EXPIRES_MINUTES: int = 15
    JWT_REFRESH_SECRET: str = "change-me-in-env-refresh"
    JWT_REFRESH_EXPIRES_DAYS: int = 14
    JWT_ISSUER: str = "booking-backend"
    REFRESH_COOKIE_NAME: str = "booking_refresh_token"
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    REFRESH_COOKIE_PATH: str = "/api/v1/auth"
    CORS_ALLOW_ORIGINS: str = "http://localhost:5173"


class LoggingConfig(Settings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"


class TelemetryConfig(Settings):
    OTEL_SDK_DISABLED: bool = False
    OTEL_TRACES_EXPORTER: Literal["console", "otlp", "none"] = "none"
    OTEL_METRICS_EXPORTER: Literal["console", "otlp", "none"] = "none"
    OTEL_LOGS_EXPORTER: Literal["console", "otlp", "none"] = "none"
    OTEL_METRIC_EXPORT_INTERVAL: int = Field(default=60_000, gt=0)


class WorkerConfig(Settings):
    DISPATCH_POLL_INTERVAL_SECONDS: int = 60
    DISPATCH_MAX_ATTEMPTS: int = 5
    DISPATCH_RETRY_BASE_SECONDS: int = 60
    DISPATCH_RETRY_MAX_BACKOFF_SECONDS: int = 3600
    REMINDER_SELECTOR_INTERVAL_SECONDS: int = 60
    BOOKING_COMPLETION_INTERVAL_SECONDS: int = 600
    BOOKING_COMPLETION_SCAN_LIMIT: int = 500
    REMINDER_LEAD_MINUTES: int = 10
    REMINDER_SCAN_LIMIT: int = 500
    WORKER_TIMEZONE: str = "Europe/Moscow"
    WORKER_MISFIRE_GRACE_TIME_SECONDS: int = 30


class EmailConfig(Settings):
    EMAIL_ENABLED: bool = False
    EMAIL_FROM: str = "noreply@booking.local"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = False
    SMTP_USE_STARTTLS: bool = False
    SMTP_TIMEOUT_SECONDS: int = 10


class S3Config(Settings):
    S3_ENDPOINT_URL: str
    S3_PUBLIC_ENDPOINT_URL: str | None = None
    S3_REGION: str
    S3_BUCKET: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_PRESIGN_EXPIRES_SECONDS: int = 900
    S3_USE_PATH_STYLE: bool = False
