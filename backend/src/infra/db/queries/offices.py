from uuid import UUID

from sqlalchemy import select

from domain.entities.office import Office
from infra.cache.decorators import cache
from infra.db.models.office import OfficeModel
from infra.db.queries.base import BaseQueryRepository
from usecases.interfaces.queries import OfficesQueryInterface


class OfficesQueryRepository(BaseQueryRepository, OfficesQueryInterface):
    @cache(key_prefix="office", return_type=Office)
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

    @cache(key_prefix="office", return_type=list[Office])
    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        city: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Office]:
        self._logger.debug("get_all_offices_query_started")
        stmt = select(OfficeModel)

        if is_active is not None:
            stmt = stmt.where(OfficeModel.is_active == is_active)
        if city is not None:
            stmt = stmt.where(OfficeModel.city == city)

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        offices = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_all_offices_query_finished count=%s",
            len(offices),
        )
        return offices
