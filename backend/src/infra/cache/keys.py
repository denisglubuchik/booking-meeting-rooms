from typing import Any

OFFICE_BY_ID_PREFIX = "office:by_id"
OFFICE_LIST_PREFIX = "office:list"
ROOM_BY_ID_PREFIX = "meeting_room:by_id"
USER_BY_ID_PREFIX = "user:by_id"


def cache_key(prefix: str, value: Any) -> str:  # noqa: ANN401
    return f"{prefix}:{value}"
