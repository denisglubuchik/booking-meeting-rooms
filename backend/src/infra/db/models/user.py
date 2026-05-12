from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.user import User, UserRole
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.booking import BookingModel
    from infra.db.models.booking_history import BookingHistoryModel
    from infra.db.models.booking_participant import BookingParticipantModel
    from infra.db.models.notification import NotificationModel
    from infra.db.models.user_session import UserSessionModel


class UserModel(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="employee")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    bookings: Mapped[list["BookingModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    history_actions: Mapped[list["BookingHistoryModel"]] = relationship(
        back_populates="performed_by_user",
        cascade="all, delete-orphan",
    )
    booking_participations: Mapped[list["BookingParticipantModel"]] = (
        relationship(
            back_populates="user",
            cascade="all, delete-orphan",
            foreign_keys="BookingParticipantModel.user_id",
        )
    )
    notifications: Mapped[list["NotificationModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["UserSessionModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            full_name=self.full_name,
            email=self.email,
            hashed_password=self.hashed_password,
            role=UserRole(self.role),
            is_active=self.is_active,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            hashed_password=user.hashed_password,
            role=UserRole(user.role),
            is_active=user.is_active,
            created_at=user.created_at,
        )
