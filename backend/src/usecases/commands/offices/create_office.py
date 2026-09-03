import logging
import uuid
from dataclasses import dataclass

from domain.entities.office import Office
from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.office import OfficeResponseDTO
from usecases.interfaces.commands import OfficesCommandRepositoryInterface


@dataclass(frozen=True, slots=True)
class CreateOfficeCommand:
    name: str
    city: str
    address: str


class CreateOfficeCommandHandler:
    def __init__(
        self,
        office_repo: OfficesCommandRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger(
            "usecases.commands.offices.create_office",
        )

    async def handle(self, command: CreateOfficeCommand) -> OfficeResponseDTO:
        self.logger.debug(
            "create_office_command_started name=%s city=%s",
            command.name,
            command.city,
        )
        async with self.office_repo:
            office = Office(
                id=uuid.uuid4(),
                name=command.name,
                city=command.city,
                address=command.address,
            )
            saved = await self.office_repo.save(office)
            self.logger.debug(
                "create_office_command_finished office_id=%s",
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
