from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.office import OfficeResponseDTO, UpdateOfficeDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBOfficesRepositoryInterface


class UpdateOfficeUseCase:
    def __init__(
        self,
        office_repo: DBOfficesRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage

    async def execute(self, dto: UpdateOfficeDTO) -> OfficeResponseDTO:
        async with self.office_repo:
            office = await self.office_repo.get_by_id(dto.id)
            if not office:
                raise NotFoundError(f"Office with id {dto.id} not found")

            office.update(name=dto.name, city=dto.city, address=dto.address)

            saved = await self.office_repo.save(office)
            image_url = None
            if saved.image_key:
                image_url = await (
                    self.file_storage.generate_presigned_download_url(
                        key=saved.image_key,
                    )
                )

            return OfficeResponseDTO(
                id=saved.id,
                name=saved.name,
                city=saved.city,
                address=saved.address,
                image_url=image_url,
                is_active=saved.is_active,
            )
