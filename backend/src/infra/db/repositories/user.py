from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, or_, select

from domain.entities.user import User
from infra.cache.decorators import cache, invalidate_cache
from infra.db.models.user import UserModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBUsersRepositoryInterface


class DBUsersRepository(
    BaseDBRepository,
    DBUsersRepositoryInterface,
):
    @invalidate_cache(key_prefix="user")
    async def save(self, user: User) -> User:
        model = UserModel.from_domain(user)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        return merged_model.to_domain()

    @invalidate_cache(key_prefix="user")
    async def delete_user(self, user: User) -> None:
        stmt = delete(UserModel).where(UserModel.id == user.id)
        await self._session.execute(stmt)

    @cache(key_prefix="user", return_type=User)
    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @cache(key_prefix="user", return_type=User)
    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def search_active(
        self,
        *,
        query: str,
        limit: int = 20,
    ) -> list[User]:
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
        return [model.to_domain() for model in result.scalars().all()]

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
        return [model.to_domain() for model in result.scalars().all()]
