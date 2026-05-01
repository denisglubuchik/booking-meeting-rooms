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
    JWT_ISSUER: str = "booking-backend"


class LoggingConfig(Settings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"
