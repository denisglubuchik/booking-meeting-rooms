# ruff: noqa: ANN401
import functools
from collections.abc import Callable
from typing import Any


def cache(key_prefix: str, return_type: type, expire: int = 3600) -> Callable:
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

            # Try to get from cache
            cached_data = await cache_service.get(key, return_type)
            if cached_data is not None:
                return cached_data

            # Miss, call original function
            result = await func(self, *args, **kwargs)

            # Save to cache if result is not None
            if result is not None:
                await cache_service.set(key, result, ttl=expire)

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
                # Try to extract the entity's ID from arguments
                entity = (
                    args[0]
                    if args
                    else kwargs.get(
                        next(iter(kwargs.keys())) if kwargs else None,
                    )
                )

                if entity and hasattr(entity, "id"):
                    key = f"{key_prefix}:{entity.id}"
                    await cache_service.delete(key)

            return result

        return wrapper

    return decorator
