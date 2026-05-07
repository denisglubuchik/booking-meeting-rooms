import logging
import uuid

from domain.entities.office import Office
from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.office import CreateOfficeDTO, OfficeResponseDTO
from usecases.interfaces.db import DBOfficesRepositoryInterface


class CreateOfficeUseCase:
    def __init__(
        self,
        office_repo: DBOfficesRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.offices.create_office")

    async def execute(self, dto: CreateOfficeDTO) -> OfficeResponseDTO:
        self.logger.debug(
            "create_office_usecase_started name=%s city=%s",
            dto.name,
            dto.city,
        )
        async with self.office_repo:
            office = Office(
                id=uuid.uuid4(),
                name=dto.name,
                city=dto.city,
                address=dto.address,
            )
            saved = await self.office_repo.save(office)
            self.logger.debug(
                "create_office_usecase_finished office_id=%s",
                saved.id,
            )
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
