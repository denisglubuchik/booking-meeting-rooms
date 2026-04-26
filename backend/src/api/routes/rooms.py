from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

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
from usecases.meeting_rooms.update_room import UpdateRoomUseCase

router = APIRouter(tags=["rooms"], route_class=DishkaRoute)


@router.get("/")
async def get_rooms(
    get_rooms_uc: FromDishka[GetAllRoomsUseCase],
    filters: Annotated[GetRoomsFilters, Query()],
) -> list[RoomResponse]:
    rooms = await get_rooms_uc.execute(filters.to_dto())
    return [RoomResponse.from_dto(room) for room in rooms]


@router.get("/{room_id}")
async def get_room(
    room_id: UUID,
    get_room_uc: FromDishka[GetRoomDetailsUseCase],
) -> RoomResponse:
    room = await get_room_uc.execute(room_id)
    return RoomResponse.from_dto(room)


@router.get("/by-office/{office_id}")
async def get_office_rooms(
    office_id: UUID,
    get_office_rooms_uc: FromDishka[GetOfficeRoomsUseCase],
    filters: Annotated[GetOfficeRoomsFilters, Query()],
) -> list[RoomResponse]:
    rooms = await get_office_rooms_uc.execute(office_id, filters.to_dto())
    return [RoomResponse.from_dto(room) for room in rooms]


@router.post("/")
async def create_room(
    payload: CreateRoomRequest,
    create_room_uc: FromDishka[CreateRoomUseCase],
) -> RoomResponse:
    room = await create_room_uc.execute(payload.to_dto())
    return RoomResponse.from_dto(room)


@router.patch("/{room_id}")
async def update_room(
    room_id: UUID,
    payload: UpdateRoomRequest,
    update_room_uc: FromDishka[UpdateRoomUseCase],
) -> RoomResponse:
    room = await update_room_uc.execute(payload.to_dto(room_id))
    return RoomResponse.from_dto(room)


@router.post("/{room_id}/activate")
async def activate_room(
    room_id: UUID,
    activate_room_uc: FromDishka[ActivateRoomUseCase],
) -> RoomResponse:
    room = await activate_room_uc.execute(room_id)
    return RoomResponse.from_dto(room)


@router.post("/{room_id}/deactivate")
async def deactivate_room(
    room_id: UUID,
    deactivate_room_uc: FromDishka[DeactivateRoomUseCase],
) -> RoomResponse:
    room = await deactivate_room_uc.execute(room_id)
    return RoomResponse.from_dto(room)
