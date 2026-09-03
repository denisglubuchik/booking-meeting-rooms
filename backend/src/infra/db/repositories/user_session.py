from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from domain.entities.user_session import UserSession
from domain.time import moscow_now
from infra.db.models.user_session import UserSessionModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.commands import UserSessionsCommandRepositoryInterface


class DBUserSessionsRepository(
    BaseDBRepository,
    UserSessionsCommandRepositoryInterface,
):
    async def save(self, session: UserSession) -> UserSession:
        self._logger.debug("save_session_started session_id=%s", session.id)
        model = UserSessionModel.from_domain(session)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        self._logger.debug(
            "save_session_finished session_id=%s",
            merged_model.id,
        )
        return merged_model.to_domain()

    async def get_active_by_id_for_update(
        self,
        session_id: UUID,
    ) -> UserSession | None:
        self._logger.debug(
            "get_active_session_started session_id=%s",
            session_id,
        )
        stmt = (
            select(UserSessionModel)
            .where(
                UserSessionModel.id == session_id,
                UserSessionModel.revoked_at.is_(None),
                UserSessionModel.expires_at > moscow_now(),
            )
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def revoke_for_user(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        revoked_at: datetime,
    ) -> None:
        stmt = select(UserSessionModel).where(
            UserSessionModel.id == session_id,
            UserSessionModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return
        model.revoked_at = revoked_at
        model.updated_at = revoked_at
        await self._session.flush()
