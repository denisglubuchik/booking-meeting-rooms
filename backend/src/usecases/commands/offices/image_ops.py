import logging
import uuid
from dataclasses import dataclass, field
from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.exceptions import BadRequest, NotFoundError
from usecases.interfaces.commands import OfficesCommandRepositoryInterface

_ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


@dataclass(frozen=True, slots=True)
class UploadOfficeImageCommand:
    office_id: UUID
    content_type: str
    data: bytes = field(repr=False)


class UploadOfficeImageCommandHandler:
    def __init__(
        self,
        office_repo: OfficesCommandRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.commands.offices.image_ops")

    async def handle(self, command: UploadOfficeImageCommand) -> None:
        self.logger.debug(
            "upload_office_image_command_started "
            "office_id=%s content_type=%s size_bytes=%s",
            command.office_id,
            command.content_type,
            len(command.data),
        )
        if command.content_type not in _ALLOWED_IMAGE_CONTENT_TYPES:
            self.logger.warning(
                "upload_office_image_unsupported_content_type "
                "office_id=%s content_type=%s",
                command.office_id,
                command.content_type,
            )
            raise BadRequest("Unsupported image content type")
        if not command.data:
            self.logger.warning(
                "upload_office_image_empty_payload office_id=%s",
                command.office_id,
            )
            raise BadRequest("Image file is empty")

        async with self.office_repo:
            office = await self.office_repo.get_by_id(command.office_id)
            if office is None:
                self.logger.warning(
                    "upload_office_image_not_found office_id=%s",
                    command.office_id,
                )
                raise NotFoundError(
                    f"Office with id={command.office_id} not found",
                )

            ext = command.content_type.split("/")[1]
            image_key = (
                f"offices/{command.office_id}/{uuid.uuid4()}.{ext}"
            )
            await self.file_storage.upload(
                key=image_key,
                data=command.data,
                content_type=command.content_type,
            )

            old_image_key = office.image_key
            office.image_key = image_key
            await self.office_repo.save(office)

            if old_image_key and old_image_key != image_key:
                await self.file_storage.delete(key=old_image_key)
            self.logger.debug(
                "upload_office_image_command_finished office_id=%s",
                command.office_id,
            )


@dataclass(frozen=True, slots=True)
class DeleteOfficeImageCommand:
    office_id: UUID


class DeleteOfficeImageCommandHandler:
    def __init__(
        self,
        office_repo: OfficesCommandRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.commands.offices.image_ops")

    async def handle(self, command: DeleteOfficeImageCommand) -> None:
        self.logger.info(
            "delete_office_image_command_started office_id=%s",
            command.office_id,
        )
        async with self.office_repo:
            office = await self.office_repo.get_by_id(command.office_id)
            if office is None:
                self.logger.warning(
                    "delete_office_image_not_found office_id=%s",
                    command.office_id,
                )
                raise NotFoundError(
                    f"Office with id={command.office_id} not found",
                )

            if office.image_key:
                await self.file_storage.delete(key=office.image_key)
                office.image_key = None
                await self.office_repo.save(office)
            self.logger.info(
                "delete_office_image_command_finished office_id=%s",
                command.office_id,
            )
