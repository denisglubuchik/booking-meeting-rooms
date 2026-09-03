import logging
from dataclasses import dataclass, field

from infra.interfaces.cache import CacheInterface


@dataclass(slots=True)
class PendingCacheInvalidations:
    keys: set[str] = field(default_factory=set)
    prefixes: set[str] = field(default_factory=set)

    def clear(self) -> None:
        self.keys.clear()
        self.prefixes.clear()


async def invalidate_cache_after_commit(
    cache: CacheInterface | None,
    invalidations: PendingCacheInvalidations,
    logger: logging.Logger,
) -> None:
    """Best-effort cache invalidation after a successful durable change."""
    pending_keys = tuple(sorted(invalidations.keys))
    pending_prefixes = tuple(sorted(invalidations.prefixes))
    invalidations.clear()

    if cache is None:
        return

    for key in pending_keys:
        try:
            await cache.delete(key)
        except Exception:
            logger.exception(
                "cache_key_invalidation_failed_after_commit key=%s",
                key,
            )

    for prefix in pending_prefixes:
        try:
            await cache.delete_by_prefix(prefix)
        except Exception:
            logger.exception(
                "cache_invalidation_failed_after_commit prefix=%s",
                prefix,
            )
