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
from usecases.commands.rooms.activate_room import (
    ActivateRoomCommand,
    ActivateRoomCommandHandler,
)
from usecases.commands.rooms.create_room import CreateRoomCommandHandler
from usecases.commands.rooms.deactivate_room import (
    DeactivateRoomCommand,
    DeactivateRoomCommandHandler,
)
from usecases.commands.rooms.image_ops import (
    DeleteRoomImageCommand,
    DeleteRoomImageCommandHandler,
    UploadRoomImageCommand,
    UploadRoomImageCommandHandler,
)
from usecases.commands.rooms.update_room import UpdateRoomCommandHandler
from usecases.queries.rooms.get_all_rooms import GetAllRoomsQueryHandler
from usecases.queries.rooms.get_office_rooms import GetOfficeRoomsQueryHandler
from usecases.queries.rooms.get_room_details import (
    GetRoomDetailsQuery,
    GetRoomDetailsQueryHandler,
)

router = APIRouter(tags=["rooms"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.rooms")


@router.get("/")
async def get_rooms(
    handler: FromDishka[GetAllRoomsQueryHandler],
    filters: Annotated[GetRoomsFilters, Query()],
    _: CurrentUserDep,
) -> list[RoomResponse]:
    logger.info(
        "get_rooms_started limit=%s offset=%s",
        filters.limit,
        filters.offset,
    )
    rooms = await handler.handle(filters.to_query())
    logger.info("get_rooms_finished count=%s", len(rooms))
    return [RoomResponse.from_dto(room) for room in rooms]


@router.get("/{room_id}")
async def get_room(
    room_id: UUID,
    handler: FromDishka[GetRoomDetailsQueryHandler],
    _: CurrentUserDep,
) -> RoomResponse:
    logger.info("get_room_started room_id=%s", room_id)
    room = await handler.handle(GetRoomDetailsQuery(room_id=room_id))
    logger.info("get_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.get("/by-office/{office_id}")
async def get_office_rooms(
    office_id: UUID,
    handler: FromDishka[GetOfficeRoomsQueryHandler],
    filters: Annotated[GetOfficeRoomsFilters, Query()],
    _: CurrentUserDep,
) -> list[RoomResponse]:
    logger.info("get_office_rooms_started office_id=%s", office_id)
    rooms = await handler.handle(filters.to_query(office_id))
    logger.info(
        "get_office_rooms_finished office_id=%s count=%s",
        office_id,
        len(rooms),
    )
    return [RoomResponse.from_dto(room) for room in rooms]


@router.post("/")
async def create_room(
    payload: CreateRoomRequest,
    handler: FromDishka[CreateRoomCommandHandler],
    _: AdminUserDep,
) -> RoomResponse:
    logger.info(
        "create_room_started office_id=%s name=%s",
        payload.office_id,
        payload.name,
    )
    room = await handler.handle(payload.to_command())
    logger.info("create_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.patch("/{room_id}")
async def update_room(
    room_id: UUID,
    payload: UpdateRoomRequest,
    handler: FromDishka[UpdateRoomCommandHandler],
    _: AdminUserDep,
) -> RoomResponse:
    logger.info("update_room_started room_id=%s", room_id)
    room = await handler.handle(payload.to_command(room_id))
    logger.info("update_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.post("/{room_id}/activate")
async def activate_room(
    room_id: UUID,
    handler: FromDishka[ActivateRoomCommandHandler],
    _: AdminUserDep,
) -> RoomResponse:
    logger.info("activate_room_started room_id=%s", room_id)
    room = await handler.handle(ActivateRoomCommand(room_id=room_id))
    logger.info("activate_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.post("/{room_id}/deactivate")
async def deactivate_room(
    room_id: UUID,
    handler: FromDishka[DeactivateRoomCommandHandler],
    _: AdminUserDep,
) -> RoomResponse:
    logger.info("deactivate_room_started room_id=%s", room_id)
    room = await handler.handle(DeactivateRoomCommand(room_id=room_id))
    logger.info("deactivate_room_finished room_id=%s", room.id)
    return RoomResponse.from_dto(room)


@router.post("/{room_id}/image", status_code=204)
async def upload_room_image(
    room_id: UUID,
    image: Annotated[UploadFile, File()],
    handler: FromDishka[UploadRoomImageCommandHandler],
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
    await handler.handle(
        UploadRoomImageCommand(
            room_id=room_id,
            content_type=content_type,
            data=data,
        ),
    )
    logger.info("upload_room_image_finished room_id=%s", room_id)


@router.delete("/{room_id}/image", status_code=204)
async def delete_room_image(
    room_id: UUID,
    handler: FromDishka[DeleteRoomImageCommandHandler],
    _: AdminUserDep,
) -> None:
    logger.info("delete_room_image_started room_id=%s", room_id)
    await handler.handle(DeleteRoomImageCommand(room_id=room_id))
    logger.info("delete_room_image_finished room_id=%s", room_id)
