from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.booking_participant import (
    BookingParticipant,
    BookingParticipantRole,
)
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.booking import BookingModel
    from infra.db.models.user import UserModel


class BookingParticipantModel(Base):
    __tablename__ = "booking_participants"
    __table_args__ = (
        UniqueConstraint(
            "booking_id",
            "user_id",
            name="uq_booking_participants_booking_user",
        ),
    )

    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    added_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    booking: Mapped["BookingModel"] = relationship(
        back_populates="participants",
    )
    user: Mapped["UserModel"] = relationship(
        back_populates="booking_participations",
        foreign_keys=[user_id],
    )
    added_by_user: Mapped["UserModel | None"] = relationship(
        foreign_keys=[added_by_user_id],
    )

    def to_domain(self) -> BookingParticipant:
        return BookingParticipant(
            id=self.id,
            booking_id=self.booking_id,
            user_id=self.user_id,
            role=BookingParticipantRole(self.role),
            added_by=self.added_by_user_id,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(
        cls,
        booking_participant: BookingParticipant,
    ) -> "BookingParticipantModel":
        return cls(
            id=booking_participant.id,
            booking_id=booking_participant.booking_id,
            user_id=booking_participant.user_id,
            role=booking_participant.role,
            added_by_user_id=booking_participant.added_by,
            created_at=booking_participant.created_at,
        )
