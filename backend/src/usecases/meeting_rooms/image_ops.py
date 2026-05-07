import logging
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
        self.logger = logging.getLogger("usecases.meeting_rooms.image_ops")

    async def execute(
        self,
        room_id: UUID,
        *,
        content_type: str,
        data: bytes,
    ) -> None:
        self.logger.debug(
            "upload_room_image_usecase_started "
            "room_id=%s content_type=%s size_bytes=%s",
            room_id,
            content_type,
            len(data),
        )
        if content_type not in _ALLOWED_IMAGE_CONTENT_TYPES:
            self.logger.warning(
                "upload_room_image_unsupported_content_type "
                "room_id=%s content_type=%s",
                room_id,
                content_type,
            )
            raise BadRequest("Unsupported image content type")
        if not data:
            self.logger.warning(
                "upload_room_image_empty_payload room_id=%s",
                room_id,
            )
            raise BadRequest("Image file is empty")

        async with self.room_repo:
            room = await self.room_repo.get_by_id(room_id)
            if room is None:
                self.logger.warning(
                    "upload_room_image_not_found room_id=%s",
                    room_id,
                )
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
            self.logger.debug(
                "upload_room_image_usecase_finished room_id=%s",
                room_id,
            )


class DeleteRoomImageUseCase:
    def __init__(
        self,
        room_repo: DBMeetingRoomsRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.meeting_rooms.image_ops")

    async def execute(self, room_id: UUID) -> None:
        self.logger.debug(
            "delete_room_image_usecase_started room_id=%s",
            room_id,
        )
        async with self.room_repo:
            room = await self.room_repo.get_by_id(room_id)
            if room is None:
                self.logger.warning(
                    "delete_room_image_not_found room_id=%s",
                    room_id,
                )
                raise NotFoundError(f"Room with id={room_id} not found")

            if room.image_key:
                await self.file_storage.delete(key=room.image_key)
                room.image_key = None
                await self.room_repo.save(room)
            self.logger.debug(
                "delete_room_image_usecase_finished room_id=%s",
                room_id,
            )
