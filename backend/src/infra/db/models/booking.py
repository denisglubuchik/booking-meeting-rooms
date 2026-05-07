from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.booking import Booking, BookingStatus, TimeRange
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.booking_history import BookingHistoryModel
    from infra.db.models.booking_participant import BookingParticipantModel
    from infra.db.models.meeting_room import MeetingRoomModel
    from infra.db.models.user import UserModel


class BookingModel(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_room_id_start_time", "room_id", "start_time"),
        Index("ix_bookings_room_id_end_time", "room_id", "end_time"),
    )

    room_id: Mapped[UUID] = mapped_column(
        ForeignKey("meeting_rooms.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    room: Mapped["MeetingRoomModel"] = relationship(back_populates="bookings")
    user: Mapped["UserModel"] = relationship(back_populates="bookings")
    history: Mapped[list["BookingHistoryModel"]] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan",
    )
    participants: Mapped[list["BookingParticipantModel"]] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan",
    )

    def to_domain(self) -> Booking:
        return Booking(
            id=self.id,
            room_id=self.room_id,
            created_by=self.user_id,
            title=self.title,
            time_range=TimeRange(
                start=self.start_time,
                end=self.end_time,
            ),
            status=BookingStatus(self.status),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, booking: Booking) -> "BookingModel":
        return cls(
            id=booking.id,
            room_id=booking.room_id,
            user_id=booking.created_by,
            title=booking.title,
            start_time=booking.time_range.start,
            end_time=booking.time_range.end,
            status=booking.status,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )
