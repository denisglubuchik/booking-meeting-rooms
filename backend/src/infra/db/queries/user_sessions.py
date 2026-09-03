from uuid import UUID

from sqlalchemy import select

from domain.entities.user_session import UserSession
from domain.time import moscow_now
from infra.db.models.user_session import UserSessionModel
from infra.db.queries.base import BaseQueryRepository
from usecases.interfaces.queries import UserSessionsQueryInterface


class UserSessionsQueryRepository(
    BaseQueryRepository,
    UserSessionsQueryInterface,
):
    async def list_by_user(
        self,
        *,
        user_id: UUID,
        is_active: bool | None = None,
    ) -> list[UserSession]:
        now = moscow_now()
        stmt = (
            select(UserSessionModel)
            .where(UserSessionModel.user_id == user_id)
            .order_by(UserSessionModel.created_at.desc())
        )
        if is_active is True:
            stmt = stmt.where(
                UserSessionModel.revoked_at.is_(None),
                UserSessionModel.expires_at > now,
            )
        if is_active is False:
            stmt = stmt.where(
                (UserSessionModel.revoked_at.is_not(None))
                | (UserSessionModel.expires_at <= now),
            )
        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]
