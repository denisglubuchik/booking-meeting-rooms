import uuid
from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.exceptions import BadRequest, NotFoundError
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface

_ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class UploadRoomImageUseCase:
    def __init__(
        self,
        room_repo: DBMeetingRoomsRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.file_storage = file_storage

    async def execute(
        self,
        room_id: UUID,
        *,
        content_type: str,
        data: bytes,
    ) -> None:
        if content_type not in _ALLOWED_IMAGE_CONTENT_TYPES:
            raise BadRequest("Unsupported image content type")
        if not data:
            raise BadRequest("Image file is empty")

        async with self.room_repo:
            room = await self.room_repo.get_by_id(room_id)
            if room is None:
                raise NotFoundError(f"Room with id={room_id} not found")

            ext = content_type.split("/")[1]
            image_key = f"rooms/{room_id}/{uuid.uuid4()}.{ext}"
            await self.file_storage.upload(
                key=image_key,
                data=data,
                content_type=content_type,
            )

            old_image_key = room.image_key
            room.image_key = image_key
            await self.room_repo.save(room)

            if old_image_key and old_image_key != image_key:
                await self.file_storage.delete(key=old_image_key)


class DeleteRoomImageUseCase:
    def __init__(
        self,
        room_repo: DBMeetingRoomsRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.file_storage = file_storage

    async def execute(self, room_id: UUID) -> None:
        async with self.room_repo:
            room = await self.room_repo.get_by_id(room_id)
            if room is None:
                raise NotFoundError(f"Room with id={room_id} not found")

            if room.image_key:
                await self.file_storage.delete(key=room.image_key)
                room.image_key = None
                await self.room_repo.save(room)
