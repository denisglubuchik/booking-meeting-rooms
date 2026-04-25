from uuid import UUID

from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBOfficesRepositoryInterface


class GetOfficeDetailsUseCase:
    def __init__(self, office_repo: DBOfficesRepositoryInterface) -> None:
        self.office_repo = office_repo

    async def execute(self, office_id: UUID) -> OfficeResponseDTO:
        office = await self.office_repo.get_by_id(office_id)
        if not office:
            raise NotFoundError(f"Office with id={office_id} not found")
        return OfficeResponseDTO(
            id=office.id,
            name=office.name,
            city=office.city,
            address=office.address,
            is_active=office.is_active,
        )
