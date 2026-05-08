from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.notification import (
    NotificationChannel,
    NotificationDispatch,
    NotificationDispatchStatus,
    NotificationType,
)
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.notification import NotificationModel
    from infra.db.models.user import UserModel


class NotificationDispatchModel(Base):
    __tablename__ = "notification_dispatch"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "type",
            "channel",
            "recipient",
            "scheduled_for",
            name="uq_notification_dispatch_dedup",
        ),
    )

    notification_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("notifications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    type: Mapped[str] = mapped_column(String(100), index=True)
    channel: Mapped[str] = mapped_column(String(20), index=True)
    recipient: Mapped[str] = mapped_column(String(320))
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(20), index=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    notification: Mapped["NotificationModel | None"] = relationship()
    user: Mapped["UserModel"] = relationship()

    def to_domain(self) -> NotificationDispatch:
        return NotificationDispatch(
            id=self.id,
            notification_id=self.notification_id,
            user_id=self.user_id,
            type=NotificationType(self.type),
            channel=NotificationChannel(self.channel),
            recipient=self.recipient,
            subject=self.subject,
            body=self.body,
            payload=self.payload,
            status=NotificationDispatchStatus(self.status),
            attempt_count=self.attempt_count,
            scheduled_for=self.scheduled_for,
            sent_at=self.sent_at,
            last_error=self.last_error,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(
        cls,
        dispatch: NotificationDispatch,
    ) -> "NotificationDispatchModel":
        return cls(
            id=dispatch.id,
            notification_id=dispatch.notification_id,
            user_id=dispatch.user_id,
            type=dispatch.type,
            channel=dispatch.channel,
            recipient=dispatch.recipient,
            subject=dispatch.subject,
            body=dispatch.body,
            payload=dispatch.payload,
            status=dispatch.status,
            attempt_count=dispatch.attempt_count,
            scheduled_for=dispatch.scheduled_for,
            sent_at=dispatch.sent_at,
            last_error=dispatch.last_error,
            created_at=dispatch.created_at,
            updated_at=dispatch.updated_at,
        )
