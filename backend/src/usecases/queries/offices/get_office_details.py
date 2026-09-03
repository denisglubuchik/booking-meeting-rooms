import logging
from dataclasses import dataclass
from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.queries import OfficesQueryInterface


@dataclass(frozen=True, slots=True)
class GetOfficeDetailsQuery:
    office_id: UUID


class GetOfficeDetailsQueryHandler:
    def __init__(
        self,
        office_repo: OfficesQueryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger(
            "usecases.queries.offices.get_office_details",
        )

    async def handle(self, query: GetOfficeDetailsQuery) -> OfficeResponseDTO:
        self.logger.debug(
            "get_office_details_query_started office_id=%s",
            query.office_id,
        )
        async with self.office_repo:
            office = await self.office_repo.get_by_id(query.office_id)
            if not office:
                self.logger.warning(
                    "get_office_details_query_not_found office_id=%s",
                    query.office_id,
                )
                raise NotFoundError(
                    f"Office with id={query.office_id} not found",
                )
            image_url = None
            if office.image_key:
                image_url = await (
                    self.file_storage.generate_presigned_download_url(
                        key=office.image_key,
                    )
                )

            self.logger.debug(
                "get_office_details_query_finished office_id=%s",
                office.id,
            )
            return OfficeResponseDTO(
                id=office.id,
                name=office.name,
                city=office.city,
                address=office.address,
                image_url=image_url,
                is_active=office.is_active,
            )
