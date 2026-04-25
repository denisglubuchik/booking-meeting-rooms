from usecases.dto.office import UpdateOfficeDTO, OfficeResponseDTO
from usecases.interfaces.db import DBOfficesRepositoryInterface
from usecases.exceptions import NotFoundError


class UpdateOfficeUseCase:
    def __init__(self, office_repo: DBOfficesRepositoryInterface) -> None:
        self.office_repo = office_repo

    async def execute(self, dto: UpdateOfficeDTO) -> OfficeResponseDTO:
        office = await self.office_repo.get_by_id(dto.id)
        if not office:
            raise NotFoundError(f"Office with id {dto.id} not found")

        office.update(name=dto.name, city=dto.city, address=dto.address)

        saved = await self.office_repo.save(office)
        return OfficeResponseDTO(
            id=saved.id,
            name=saved.name,
            city=saved.city,
            address=saved.address,
            is_active=saved.is_active,
        )
