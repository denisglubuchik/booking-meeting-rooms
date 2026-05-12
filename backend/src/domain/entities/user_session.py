from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.time import moscow_now


@dataclass(slots=True, kw_only=True)
class UserSession:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None
    user_agent: str | None = None
    ip: str | None = None
    created_at: datetime = field(default_factory=moscow_now)
    updated_at: datetime = field(default_factory=moscow_now)
