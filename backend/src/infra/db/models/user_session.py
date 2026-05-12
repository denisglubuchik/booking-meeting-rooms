from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.user_session import UserSession
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.user import UserModel


class UserSessionModel(Base):
    __tablename__ = "user_sessions"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    refresh_token_hash: Mapped[str] = mapped_column(
        String(255),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_agent: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["UserModel"] = relationship(back_populates="sessions")

    def to_domain(self) -> UserSession:
        return UserSession(
            id=self.id,
            user_id=self.user_id,
            refresh_token_hash=self.refresh_token_hash,
            expires_at=self.expires_at,
            revoked_at=self.revoked_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
            user_agent=self.user_agent,
            ip=self.ip,
        )

    @classmethod
    def from_domain(cls, session: UserSession) -> "UserSessionModel":
        return cls(
            id=session.id,
            user_id=session.user_id,
            refresh_token_hash=session.refresh_token_hash,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
            created_at=session.created_at,
            updated_at=session.updated_at,
            user_agent=session.user_agent,
            ip=session.ip,
        )
