import logging
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, File, Query, UploadFile

from api.dependencies.auth import AdminUserDep, CurrentUserDep
from api.schemas.rooms import (
    CreateRoomRequest,
    GetOfficeRoomsFilters,
    GetRoomsFilters,
    RoomResponse,
    UpdateRoomRequest,
)
from usecases.meeting_rooms.activate_room import ActivateRoomUseCase
from usecases.meeting_rooms.create_room import CreateRoomUseCase
from usecases.meeting_rooms.deactivate_room import DeactivateRoomUseCase
from usecases.meeting_rooms.get_all_rooms import GetAllRoomsUseCase
from usecases.meeting_rooms.get_office_rooms import GetOfficeRoomsUseCase
from usecases.meeting_rooms.get_room_details import GetRoomDetailsUseCase
from usecases.meeting_rooms.image_ops import (
    DeleteRoomImageUseCase,
    UploadRoomImageUseCase,
)
from usecases.meeting_rooms.update_room import UpdateRoomUseCase

router = APIRouter(tags=["rooms"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.rooms")


@router.get("/")
async def get_rooms(
    get_rooms_uc: FromDishka[GetAllRoomsUseCase],
    filters: Annotated[GetRoomsFilters, Query()],
    _: CurrentUserDep,
) -> list[RoomResponse]:
    logger.info(
        "get_rooms_started limit=%s offset=%s",
        filters.limit,
        filters.offset,
    )
    rooms = await get_rooms_uc.execute(filters.to_dto())
    logger.info("get_rooms_finished count=%s", len(rooms))
    return [RoomResponse.from_dto(room) for room in rooms]


@router.get("/{room_id}")
async def get_room(
    room_id: UUID,
    get_room_uc: FromDishka[GetRoomDetailsUseCase],
    _: CurrentUserDep,
) -> RoomResponse:
    logger.info("get_room_started room_id=%s", room_id)
    room = await get_room_uc.execute(room_id)
    logger.info("get_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.get("/by-office/{office_id}")
async def get_office_rooms(
    office_id: UUID,
    get_office_rooms_uc: FromDishka[GetOfficeRoomsUseCase],
    filters: Annotated[GetOfficeRoomsFilters, Query()],
    _: CurrentUserDep,
) -> list[RoomResponse]:
    logger.info("get_office_rooms_started office_id=%s", office_id)
    rooms = await get_office_rooms_uc.execute(office_id, filters.to_dto())
    logger.info(
        "get_office_rooms_finished office_id=%s count=%s",
        office_id,
        len(rooms),
    )
    return [RoomResponse.from_dto(room) for room in rooms]


@router.post("/")
async def create_room(
    payload: CreateRoomRequest,
    create_room_uc: FromDishka[CreateRoomUseCase],
    _: AdminUserDep,
) -> RoomResponse:
    logger.info(
        "create_room_started office_id=%s name=%s",
        payload.office_id,
        payload.name,
    )
    room = await create_room_uc.execute(payload.to_dto())
    logger.info("create_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.patch("/{room_id}")
async def update_room(
    room_id: UUID,
    payload: UpdateRoomRequest,
    update_room_uc: FromDishka[UpdateRoomUseCase],
    _: AdminUserDep,
) -> RoomResponse:
    logger.info("update_room_started room_id=%s", room_id)
    room = await update_room_uc.execute(payload.to_dto(room_id))
    logger.info("update_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.post("/{room_id}/activate")
async def activate_room(
    room_id: UUID,
    activate_room_uc: FromDishka[ActivateRoomUseCase],
    _: AdminUserDep,
) -> RoomResponse:
    logger.info("activate_room_started room_id=%s", room_id)
    room = await activate_room_uc.execute(room_id)
    logger.info("activate_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.post("/{room_id}/deactivate")
async def deactivate_room(
    room_id: UUID,
    deactivate_room_uc: FromDishka[DeactivateRoomUseCase],
    _: AdminUserDep,
) -> RoomResponse:
    logger.info("deactivate_room_started room_id=%s", room_id)
    room = await deactivate_room_uc.execute(room_id)
    logger.info("deactivate_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.post("/{room_id}/image", status_code=204)
async def upload_room_image(
    room_id: UUID,
    image: Annotated[UploadFile, File()],
    upload_image_uc: FromDishka[UploadRoomImageUseCase],
    _: AdminUserDep,
) -> None:
    content_type = image.content_type or ""
    data = await image.read()
    logger.info(
        "upload_room_image_started room_id=%s content_type=%s size_bytes=%s",
        room_id,
        content_type,
        len(data),
    )
    await upload_image_uc.execute(
        room_id,
        content_type=content_type,
        data=data,
    )
    logger.info("upload_room_image_finished room_id=%s", room_id)


@router.delete("/{room_id}/image", status_code=204)
async def delete_room_image(
    room_id: UUID,
    delete_image_uc: FromDishka[DeleteRoomImageUseCase],
    _: AdminUserDep,
) -> None:
    logger.info("delete_room_image_started room_id=%s", room_id)
    await delete_image_uc.execute(room_id)
    logger.info("delete_room_image_finished room_id=%s", room_id)
