import uuid
from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.exceptions import BadRequest, NotFoundError
from usecases.interfaces.db import DBOfficesRepositoryInterface

_ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class UploadOfficeImageUseCase:
    def __init__(
        self,
        office_repo: DBOfficesRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage

    async def execute(
        self,
        office_id: UUID,
        *,
        content_type: str,
        data: bytes,
    ) -> None:
        if content_type not in _ALLOWED_IMAGE_CONTENT_TYPES:
            raise BadRequest("Unsupported image content type")
        if not data:
            raise BadRequest("Image file is empty")

        async with self.office_repo:
            office = await self.office_repo.get_by_id(office_id)
            if office is None:
                raise NotFoundError(f"Office with id={office_id} not found")

            ext = content_type.split("/")[1]
            image_key = f"offices/{office_id}/{uuid.uuid4()}.{ext}"
            await self.file_storage.upload(
                key=image_key,
                data=data,
                content_type=content_type,
            )

            old_image_key = office.image_key
            office.image_key = image_key
            await self.office_repo.save(office)

            if old_image_key and old_image_key != image_key:
                await self.file_storage.delete(key=old_image_key)


class DeleteOfficeImageUseCase:
    def __init__(
        self,
        office_repo: DBOfficesRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.office_repo = office_repo
        self.file_storage = file_storage

    async def execute(self, office_id: UUID) -> None:
        async with self.office_repo:
            office = await self.office_repo.get_by_id(office_id)
            if office is None:
                raise NotFoundError(f"Office with id={office_id} not found")

            if office.image_key:
                await self.file_storage.delete(key=office.image_key)
                office.image_key = None
                await self.office_repo.save(office)
