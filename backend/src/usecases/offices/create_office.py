import uuid

from domain.entities.office import Office
from usecases.dto.office import CreateOfficeDTO, OfficeResponseDTO
from usecases.interfaces.db import DBOfficesRepositoryInterface


class CreateOfficeUseCase:
    def __init__(self, office_repo: DBOfficesRepositoryInterface) -> None:
        self.office_repo = office_repo

    async def execute(self, dto: CreateOfficeDTO) -> OfficeResponseDTO:
        async with self.office_repo:
            office = Office(
                id=uuid.uuid4(),
                name=dto.name,
                city=dto.city,
                address=dto.address,
            )
            saved = await self.office_repo.save(office)

            return OfficeResponseDTO(
                id=saved.id,
                name=saved.name,
                city=saved.city,
                address=saved.address,
                is_active=saved.is_active,
            )
