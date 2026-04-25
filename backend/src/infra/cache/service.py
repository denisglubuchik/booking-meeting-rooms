from typing import Any, TypeVar

from pydantic import TypeAdapter
from redis.asyncio import Redis

from core.config import RedisConfig
from infra.interfaces.cache import CacheInterface

T = TypeVar("T")


class RedisCacheService(CacheInterface):
    def __init__(self, redis_config: RedisConfig) -> None:
        self.prefix = redis_config.APP_REDIS_PREFIX
        self.redis = Redis(
            host=redis_config.REDIS_HOST,
            port=redis_config.REDIS_PORT,
            password=redis_config.REDIS_PASSWORD,
            username=redis_config.REDIS_USER,
            db=redis_config.REDIS_DB,
            decode_responses=True,
        )

    def _make_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    @staticmethod
    def _serialize(value: Any) -> str:  # noqa: ANN401
        return TypeAdapter(type(value)).dump_json(value).decode("utf-8")

    @staticmethod
    def _deserialize(data: str, return_type: type[T]) -> T:
        return TypeAdapter(return_type).validate_json(data)

    async def get(self, key: str, return_type: type[T]) -> T | None:
        data = await self.redis.get(self._make_key(key))
        if data is None:
            return None
        try:
            return self._deserialize(data, return_type)
        except Exception:  # noqa: BLE001
            # Return None if deserialization fails (e.g. format changed)
            return None

    async def set(
        self,
        key: str,
        value: Any,  # noqa: ANN401
        ttl: int = 3600,
    ) -> None:
        serialized = self._serialize(value)
        await self.redis.set(self._make_key(key), serialized, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(self._make_key(key))
