import logging
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
        self._logger = logging.getLogger("infra.cache.redis")
        self._logger.info(
            "redis_cache_initialized host=%s port=%s db=%s",
            redis_config.REDIS_HOST,
            redis_config.REDIS_PORT,
            redis_config.REDIS_DB,
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
        self._logger.debug("redis_get_started key=%s", key)
        data = await self.redis.get(self._make_key(key))
        if data is None:
            self._logger.debug("redis_get_miss key=%s", key)
            return None
        try:
            value = self._deserialize(data, return_type)
            self._logger.debug("redis_get_hit key=%s", key)
            return value
        except Exception:  # noqa: BLE001
            # Return None if deserialization fails (e.g. format changed)
            self._logger.warning("redis_get_deserialize_failed key=%s", key)
            return None

    async def set(
        self,
        key: str,
        value: Any,  # noqa: ANN401
        ttl: int = 3600,
    ) -> None:
        self._logger.debug("redis_set key=%s ttl=%s", key, ttl)
        serialized = self._serialize(value)
        await self.redis.set(self._make_key(key), serialized, ex=ttl)

    async def delete(self, key: str) -> None:
        self._logger.debug("redis_delete key=%s", key)
        await self.redis.delete(self._make_key(key))

    async def delete_by_prefix(self, prefix: str) -> None:
        self._logger.debug("redis_delete_by_prefix_started prefix=%s", prefix)
        exact_key = self._make_key(prefix)
        pattern = self._make_key(f"{prefix}:*")
        keys = [exact_key]

        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)  # noqa: PERF401

        await self.redis.delete(*keys)
        self._logger.debug("redis_delete_by_prefix_finished prefix=%s keys=%s", prefix, len(keys))
