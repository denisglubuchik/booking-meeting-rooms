from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.notification import (
    Notification,
    NotificationType,
)
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.user import UserModel


class NotificationModel(Base):
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    type: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    user: Mapped["UserModel"] = relationship(back_populates="notifications")

    def to_domain(self) -> Notification:
        return Notification(
            id=self.id,
            user_id=self.user_id,
            type=NotificationType(self.type),
            title=self.title,
            body=self.body,
            payload=self.payload,
            created_at=self.created_at,
            read_at=self.read_at,
        )

    @classmethod
    def from_domain(cls, notification: Notification) -> "NotificationModel":
        return cls(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            body=notification.body,
            payload=notification.payload,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )
