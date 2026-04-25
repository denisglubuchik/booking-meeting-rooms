from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.booking_history import BookingHistory, HistoryAction
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.booking import BookingModel
    from infra.db.models.user import UserModel


class BookingHistoryModel(Base):
    __tablename__ = "booking_history"

    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
    )
    action: Mapped[str] = mapped_column(String(50))
    performed_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    details: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    booking: Mapped["BookingModel"] = relationship(back_populates="history")
    performed_by_user: Mapped["UserModel"] = relationship(
        back_populates="history_actions",
    )

    def to_domain(self) -> BookingHistory:
        return BookingHistory(
            id=self.id,
            booking_id=self.booking_id,
            action=HistoryAction(self.action),
            performed_by=self.performed_by_user_id,
            details=self.details,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(
        cls,
        booking_history: BookingHistory,
    ) -> "BookingHistoryModel":
        return cls(
            id=booking_history.id,
            booking_id=booking_history.booking_id,
            action=booking_history.action,
            performed_by_user_id=booking_history.performed_by,
            details=booking_history.details,
            created_at=booking_history.created_at,
        )
