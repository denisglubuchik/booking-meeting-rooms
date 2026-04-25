from usecases.dto.office import OfficeResponseDTO, OfficeFiltersDTO
from usecases.interfaces.db import DBOfficesRepositoryInterface


class GetOfficesUseCase:
    def __init__(self, office_repo: DBOfficesRepositoryInterface) -> None:
        self.office_repo = office_repo

    async def execute(
        self, filters: OfficeFiltersDTO | None = None
    ) -> list[OfficeResponseDTO]:
        filters = filters or OfficeFiltersDTO()
        offices = await self.office_repo.get_all(
            is_active=filters.is_active,
            city=filters.city,
            limit=filters.limit,
            offset=filters.offset,
        )
        return [
            OfficeResponseDTO(
                id=office.id,
                name=office.name,
                city=office.city,
                address=office.address,
                is_active=office.is_active,
            )
            for office in offices
        ]
