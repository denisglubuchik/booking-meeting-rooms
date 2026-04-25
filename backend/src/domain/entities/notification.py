from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.time import moscow_now


@dataclass(slots=True, kw_only=True)
class Notification:
    id: UUID
    user_id: UUID
    message: str
    is_sent: bool = False
    created_at: datetime = field(default_factory=moscow_now)

    def mark_sent(self) -> None:
        self.is_sent = True
