from uuid import UUID

from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBOfficesRepositoryInterface


class DeactivateOfficeUseCase:
    def __init__(self, office_repo: DBOfficesRepositoryInterface) -> None:
        self.office_repo = office_repo

    async def execute(self, office_id: UUID) -> OfficeResponseDTO:
        async with self.office_repo:
            office = await self.office_repo.get_by_id(office_id)
            if not office:
                raise NotFoundError(f"Office with id {office_id} not found")

            office.deactivate()

            saved = await self.office_repo.save(office)

            return OfficeResponseDTO(
                id=saved.id,
                name=saved.name,
                city=saved.city,
                address=saved.address,
                is_active=saved.is_active,
            )
