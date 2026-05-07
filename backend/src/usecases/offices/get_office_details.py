from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBOfficesRepositoryInterface


class GetOfficeDetailsUseCase:
    def __init__(
        self,
        office_repo: DBOfficesRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage

    async def execute(self, office_id: UUID) -> OfficeResponseDTO:
        async with self.office_repo:
            office = await self.office_repo.get_by_id(office_id)
            if not office:
                raise NotFoundError(f"Office with id={office_id} not found")
            image_url = None
            if office.image_key:
                image_url = await (
                    self.file_storage.generate_presigned_download_url(
                        key=office.image_key,
                    )
                )

            return OfficeResponseDTO(
                id=office.id,
                name=office.name,
                city=office.city,
                address=office.address,
                image_url=image_url,
                is_active=office.is_active,
            )
