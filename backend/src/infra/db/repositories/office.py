from uuid import UUID

from sqlalchemy import delete, select

from domain.entities.office import Office
from infra.cache.decorators import cache, invalidate_cache
from infra.db.models.office import OfficeModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBOfficesRepositoryInterface


class DBOfficesRepository(
    BaseDBRepository,
    DBOfficesRepositoryInterface,
):
    @invalidate_cache(key_prefix="office")
    async def save(self, office: Office) -> Office:
        model = OfficeModel.from_domain(office)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        return merged_model.to_domain()

    @invalidate_cache(key_prefix="office")
    async def delete_office(self, office: Office) -> None:
        stmt = delete(OfficeModel).where(OfficeModel.id == office.id)
        await self._session.execute(stmt)

    @cache(key_prefix="office", return_type=Office)
    async def get_by_id(self, office_id: UUID) -> Office | None:
        stmt = select(OfficeModel).where(OfficeModel.id == office_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @cache(key_prefix="office", return_type=list[Office])
    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        city: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Office]:
        stmt = select(OfficeModel)

        if is_active is not None:
            stmt = stmt.where(OfficeModel.is_active == is_active)
        if city is not None:
            stmt = stmt.where(OfficeModel.city == city)

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]
