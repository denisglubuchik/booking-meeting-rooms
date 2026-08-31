from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DBConfig(Settings):
    PG_PORT: int = 5432
    PG_DB: str
    PG_USER: str
    PG_PASS: str
    PG_HOST: str

    @property
    def DATABASE_URL(self) -> str:  # noqa
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


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
