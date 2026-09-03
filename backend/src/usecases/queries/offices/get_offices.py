import logging
from dataclasses import dataclass

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.office import OfficeResponseDTO
from usecases.interfaces.queries import OfficesQueryInterface


@dataclass(frozen=True, slots=True)
class GetOfficesQuery:
    is_active: bool | None = None
    city: str | None = None
    limit: int = 100
    offset: int = 0


class GetOfficesQueryHandler:
    def __init__(
        self,
        office_repo: OfficesQueryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.queries.offices.get_offices")

    async def handle(
        self,
        query: GetOfficesQuery,
    ) -> list[OfficeResponseDTO]:
        self.logger.debug("get_offices_query_started")
        async with self.office_repo:
            offices = await self.office_repo.get_all(
                is_active=query.is_active,
                city=query.city,
                limit=query.limit,
                offset=query.offset,
            )
            self.logger.debug(
                "get_offices_query_fetched count=%s",
                len(offices),
            )

            output: list[OfficeResponseDTO] = []
            for office in offices:
                image_url = None
                if office.image_key:
                    image_url = (
                        await self.file_storage.generate_presigned_download_url(
                            key=office.image_key,
                        )
                    )
                output.append(
                    OfficeResponseDTO(
                        id=office.id,
                        name=office.name,
                        city=office.city,
                        address=office.address,
                        image_url=image_url,
                        is_active=office.is_active,
                    ),
                )

            self.logger.debug(
                "get_offices_query_finished count=%s",
                len(output),
            )
            return output
