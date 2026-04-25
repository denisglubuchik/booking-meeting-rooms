from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from domain.time import moscow_now


class HistoryAction(StrEnum):
    CREATED = "created"
    CANCELLED = "cancelled"
    UPDATED = "updated"
    RESCHEDULED = "rescheduled"


@dataclass(slots=True, kw_only=True)
class BookingHistory:
    id: UUID
    booking_id: UUID
    action: HistoryAction
    performed_by: UUID
    details: str = ""
    created_at: datetime = field(default_factory=moscow_now)
