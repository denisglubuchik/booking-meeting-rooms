import logging

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.office import OfficeFiltersDTO, OfficeResponseDTO
from usecases.interfaces.db import DBOfficesRepositoryInterface


class GetOfficesUseCase:
    def __init__(
        self,
        office_repo: DBOfficesRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.offices.get_offices")

    async def execute(
        self,
        filters: OfficeFiltersDTO | None = None,
    ) -> list[OfficeResponseDTO]:
        self.logger.debug("get_offices_usecase_started")
        async with self.office_repo:
            filters = filters or OfficeFiltersDTO()
            offices = await self.office_repo.get_all(
                is_active=filters.is_active,
                city=filters.city,
                limit=filters.limit,
                offset=filters.offset,
            )
            self.logger.debug("get_offices_usecase_fetched count=%s", len(offices))

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

            self.logger.debug("get_offices_usecase_finished count=%s", len(output))
            return output
