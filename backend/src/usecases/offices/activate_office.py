import logging
from uuid import UUID

from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBOfficesRepositoryInterface


class ActivateOfficeUseCase:
    def __init__(self, office_repo: DBOfficesRepositoryInterface) -> None:
        self.office_repo = office_repo
        self.logger = logging.getLogger("usecases.offices.activate_office")

    async def execute(self, office_id: UUID) -> OfficeResponseDTO:
        self.logger.debug("activate_office_usecase_started office_id=%s", office_id)
        async with self.office_repo:
            office = await self.office_repo.get_by_id(office_id)
            if not office:
                self.logger.warning(
                    "activate_office_usecase_not_found office_id=%s",
                    office_id,
                )
                raise NotFoundError(f"Office with id {office_id} not found")

            office.activate()

            saved = await self.office_repo.save(office)
            self.logger.debug(
                "activate_office_usecase_finished office_id=%s",
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
