# ruff: noqa: ANN401
import functools
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("infra.cache.decorators")


def cache(
    key_prefix: str,
    return_type: type,
    expire: int | Callable[[Any], int] = 3600,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            cache_service = getattr(self, "cache", None)

            if cache_service is None:
                # Normal execution if no cache service is provided
                return await func(self, *args, **kwargs)

            # Create a unique key string
            key_parts = [str(a) for a in args]
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in kwargs.items())
            key = (
                f"{key_prefix}:{':'.join(key_parts)}"
                if key_parts
                else key_prefix
            )
            logger.info("cache_lookup_started key_prefix=%s", key_prefix)

            # Try to get from cache
            cached_data = await cache_service.get(key, return_type)
            if cached_data is not None:
                logger.info("cache_hit key_prefix=%s", key_prefix)
                return cached_data

            # Miss, call original function
            logger.info("cache_miss key_prefix=%s", key_prefix)
            result = await func(self, *args, **kwargs)

            # Save to cache if result is not None
            if result is not None:
                ttl = expire(self) if callable(expire) else expire
                await cache_service.set(key, result, ttl=ttl)
                logger.info(
                    "cache_set key_prefix=%s ttl=%s",
                    key_prefix,
                    ttl,
                )

            return result

        return wrapper

    return decorator


def invalidate_cache(key_prefix: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            result = await func(self, *args, **kwargs)

            cache_service = getattr(self, "cache", None)
            if cache_service is not None:
                logger.info("cache_invalidate_by_prefix prefix=%s", key_prefix)
                await cache_service.delete_by_prefix(key_prefix)

            return result

        return wrapper

    return decorator
