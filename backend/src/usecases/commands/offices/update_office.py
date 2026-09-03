import logging
from dataclasses import dataclass
from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.commands import OfficesCommandRepositoryInterface


@dataclass(frozen=True, slots=True)
class UpdateOfficeCommand:
    office_id: UUID
    name: str | None = None
    city: str | None = None
    address: str | None = None


class UpdateOfficeCommandHandler:
    def __init__(
        self,
        office_repo: OfficesCommandRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger(
            "usecases.commands.offices.update_office",
        )

    async def handle(self, command: UpdateOfficeCommand) -> OfficeResponseDTO:
        self.logger.debug(
            "update_office_command_started office_id=%s",
            command.office_id,
        )
        async with self.office_repo:
            office = await self.office_repo.get_by_id(command.office_id)
            if not office:
                self.logger.warning(
                    "update_office_command_not_found office_id=%s",
                    command.office_id,
                )
                raise NotFoundError(
                    f"Office with id {command.office_id} not found",
                )

            office.update(
                name=command.name,
                city=command.city,
                address=command.address,
            )

            saved = await self.office_repo.save(office)
            self.logger.debug(
                "update_office_command_finished office_id=%s",
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
