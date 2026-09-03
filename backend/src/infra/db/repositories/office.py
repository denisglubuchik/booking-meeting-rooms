from uuid import UUID

from sqlalchemy import delete, select

from domain.entities.office import Office
from infra.cache.keys import (
    OFFICE_BY_ID_PREFIX,
    OFFICE_LIST_PREFIX,
    cache_key,
)
from infra.db.models.office import OfficeModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBOfficesRepositoryInterface


class DBOfficesRepository(
    BaseDBRepository,
    DBOfficesRepositoryInterface,
):
    async def save(self, office: Office) -> Office:
        self._logger.debug("save_office_started office_id=%s", office.id)
        model = OfficeModel.from_domain(office)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        self.mark_cache_key_dirty(cache_key(OFFICE_BY_ID_PREFIX, office.id))
        self.mark_cache_prefix_dirty(OFFICE_LIST_PREFIX)
        self._logger.debug("save_office_finished office_id=%s", merged_model.id)
        return merged_model.to_domain()

    async def delete_office(self, office: Office) -> None:
        self._logger.debug("delete_office_started office_id=%s", office.id)
        stmt = delete(OfficeModel).where(OfficeModel.id == office.id)
        await self._session.execute(stmt)
        self.mark_cache_key_dirty(cache_key(OFFICE_BY_ID_PREFIX, office.id))
        self.mark_cache_prefix_dirty(OFFICE_LIST_PREFIX)
        self._logger.debug("delete_office_finished office_id=%s", office.id)

    async def get_by_id(self, office_id: UUID) -> Office | None:
        self._logger.debug("get_office_by_id_started office_id=%s", office_id)
        stmt = select(OfficeModel).where(OfficeModel.id == office_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "get_office_by_id_finished office_id=%s found=%s",
            office_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        city: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Office]:
        self._logger.debug("get_all_offices_repository_started")
        stmt = select(OfficeModel)

        if is_active is not None:
            stmt = stmt.where(OfficeModel.is_active == is_active)
        if city is not None:
            stmt = stmt.where(OfficeModel.city == city)

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        offices = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_all_offices_repository_finished count=%s",
            len(offices),
        )
        return offices
