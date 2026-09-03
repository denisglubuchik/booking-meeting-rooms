from datetime import datetime
from uuid import UUID

from sqlalchemy import or_, select

from domain.entities.user import User
from infra.cache.decorators import cache
from infra.cache.keys import USER_BY_ID_PREFIX
from infra.db.models.user import UserModel
from infra.db.queries.base import BaseQueryRepository
from usecases.interfaces.queries import UsersQueryInterface


class UsersQueryRepository(BaseQueryRepository, UsersQueryInterface):
    @cache(key_prefix=USER_BY_ID_PREFIX, return_type=User)
    async def get_by_id(self, user_id: UUID) -> User | None:
        self._logger.debug("get_user_by_id_started user_id=%s", user_id)
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "get_user_by_id_finished user_id=%s found=%s",
            user_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def search_active(
        self,
        *,
        query: str,
        limit: int = 20,
    ) -> list[User]:
        self._logger.debug(
            "search_active_users_started query=%s limit=%s",
            query,
            limit,
        )
        pattern = f"%{query}%"
        stmt = (
            select(UserModel)
            .where(
                UserModel.is_active.is_(True),
                or_(
                    UserModel.full_name.ilike(pattern),
                    UserModel.email.ilike(pattern),
                ),
            )
            .order_by(UserModel.full_name)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        users = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug("search_active_users_finished count=%s", len(users))
        return users

    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        role: str | None = None,
        created_at_gte: datetime | None = None,
        created_at_lte: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[User]:
        self._logger.debug("get_all_users_query_started")
        stmt = select(UserModel)

        if is_active is not None:
            stmt = stmt.where(UserModel.is_active == is_active)
        if role is not None:
            stmt = stmt.where(UserModel.role == role)
        if created_at_gte is not None:
            stmt = stmt.where(UserModel.created_at >= created_at_gte)
        if created_at_lte is not None:
            stmt = stmt.where(UserModel.created_at <= created_at_lte)

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        users = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug("get_all_users_query_finished count=%s", len(users))
        return users
