from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from domain.time import moscow_now


class BookingParticipantRole(StrEnum):
    ORGANIZER = "organizer"
    PARTICIPANT = "participant"


@dataclass(slots=True, kw_only=True)
class BookingParticipant:
    id: UUID
    booking_id: UUID
    user_id: UUID
    role: BookingParticipantRole = BookingParticipantRole.PARTICIPANT
    added_by: UUID | None = None
    created_at: datetime = field(default_factory=moscow_now)
