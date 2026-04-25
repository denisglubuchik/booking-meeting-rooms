from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    PG_PORT: int = 5432
    PG_DB: str
    PG_USER: str
    PG_PASS: str
    PG_HOST: str

    @property
    def DATABASE_URL(self) -> str:  # noqa
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


class RedisConfig(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_USER: str
    REDIS_DB: int
    APP_REDIS_PREFIX: str = "booking:back"
