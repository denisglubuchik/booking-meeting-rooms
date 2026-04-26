from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class CacheInterface(Protocol):
    async def get(self, key: str, return_type: type[T]) -> T | None:
        """Get value from cache and deserialize to return_type."""
        ...

    async def set(
        self,
        key: str,
        value: Any,  # noqa: ANN401
        ttl: int = 3600,
    ) -> None:
        """Serialize value and set in cache with expiration (seconds)."""
        ...

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        ...

    async def delete_by_prefix(self, prefix: str) -> None:
        """Delete all keys by logical prefix."""
        ...
