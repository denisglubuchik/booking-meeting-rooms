import logging
from dataclasses import dataclass
from uuid import UUID

from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.commands import OfficesCommandRepositoryInterface


@dataclass(frozen=True, slots=True)
class ActivateOfficeCommand:
    office_id: UUID


class ActivateOfficeCommandHandler:
    def __init__(self, office_repo: OfficesCommandRepositoryInterface) -> None:
        self.office_repo = office_repo
        self.logger = logging.getLogger(
            "usecases.commands.offices.activate_office",
        )

    async def handle(self, command: ActivateOfficeCommand) -> OfficeResponseDTO:
        self.logger.debug(
            "activate_office_command_started office_id=%s",
            command.office_id,
        )
        async with self.office_repo:
            office = await self.office_repo.get_by_id(command.office_id)
            if not office:
                self.logger.warning(
                    "activate_office_command_not_found office_id=%s",
                    command.office_id,
                )
                raise NotFoundError(
                    f"Office with id {command.office_id} not found",
                )

            office.activate()

            saved = await self.office_repo.save(office)
            self.logger.debug(
                "activate_office_command_finished office_id=%s",
                saved.id,
            )

            return OfficeResponseDTO(
                id=saved.id,
                name=saved.name,
                city=saved.city,
                address=saved.address,
                image_url=None,
                is_active=saved.is_active,
            )
