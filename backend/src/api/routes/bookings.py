from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from api.dependencies.auth import AdminUserDep, CurrentUserDep
from api.schemas.bookings import (
    BookingResponse,
    ChangeRoomBookingRequest,
    CreateBookingRequest,
    GetAvailableRoomsFilters,
    GetBookingsFilters,
    RescheduleBookingRequest,
)
from api.schemas.rooms import RoomResponse
from usecases.bookings.cancel_booking import CancelBookingUseCase
from usecases.bookings.change_room import ChangeRoomBookingUseCase
from usecases.bookings.create_booking import CreateBookingUseCase
from usecases.bookings.get_all_bookings import GetAllBookingsUseCase
from usecases.bookings.get_available_rooms import GetAvailableRoomsUseCase
from usecases.bookings.get_booking_details import GetBookingDetailsUseCase
from usecases.bookings.get_my_bookings import GetMyBookingsUseCase
from usecases.bookings.get_room_bookings import GetRoomBookingsUseCase
from usecases.bookings.reschedule_booking import RescheduleBookingUseCase
from usecases.dto.booking import CancelBookingDTO

router = APIRouter(tags=["bookings"], route_class=DishkaRoute)


@router.get("/")
async def get_bookings(
    get_bookings_uc: FromDishka[GetAllBookingsUseCase],
    filters: Annotated[GetBookingsFilters, Query()],
    _: AdminUserDep,
) -> list[BookingResponse]:
    bookings = await get_bookings_uc.execute(filters.to_dto())
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/available-rooms")
async def get_available_rooms(
    get_available_rooms_uc: FromDishka[GetAvailableRoomsUseCase],
    filters: Annotated[GetAvailableRoomsFilters, Query()],
    _: CurrentUserDep,
) -> list[RoomResponse]:
    rooms = await get_available_rooms_uc.execute(filters.to_dto())
    return [RoomResponse.from_dto(room) for room in rooms]


@router.get("/by-room/{room_id}")
async def get_room_bookings(
    room_id: UUID,
    get_room_bookings_uc: FromDishka[GetRoomBookingsUseCase],
    filters: Annotated[GetBookingsFilters, Query()],
    _: CurrentUserDep,
) -> list[BookingResponse]:
    bookings = await get_room_bookings_uc.execute(
        filters.to_dto(room_id=room_id),
    )
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/by-user/{user_id}")
async def get_user_bookings(
    user_id: UUID,
    get_user_bookings_uc: FromDishka[GetMyBookingsUseCase],
    filters: Annotated[GetBookingsFilters, Query()],
    _: AdminUserDep,
) -> list[BookingResponse]:
    bookings = await get_user_bookings_uc.execute(
        filters.to_dto(user_id=user_id),
    )
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/my-bookings")
async def get_my_bookings(
    get_user_bookings_uc: FromDishka[GetMyBookingsUseCase],
    filters: Annotated[GetBookingsFilters, Query()],
    current_user: CurrentUserDep,
) -> list[BookingResponse]:
    bookings = await get_user_bookings_uc.execute(
        filters.to_dto(user_id=current_user.id),
    )
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/{booking_id}")
async def get_booking(
    booking_id: UUID,
    get_booking_uc: FromDishka[GetBookingDetailsUseCase],
) -> BookingResponse:
    booking = await get_booking_uc.execute(booking_id)
    return BookingResponse.from_dto(booking)


@router.post("/")
async def create_booking(
    payload: CreateBookingRequest,
    create_booking_uc: FromDishka[CreateBookingUseCase],
    current_user: CurrentUserDep,
) -> BookingResponse:
    booking = await create_booking_uc.execute(
        payload.to_dto(created_by=current_user.id),
    )
    return BookingResponse.from_dto(booking)


@router.patch("/{booking_id}/reschedule")
async def reschedule_booking(
    booking_id: UUID,
    payload: RescheduleBookingRequest,
    reschedule_booking_uc: FromDishka[RescheduleBookingUseCase],
    current_user: CurrentUserDep,
) -> BookingResponse:
    booking = await reschedule_booking_uc.execute(
        payload.to_dto(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    return BookingResponse.from_dto(booking)


@router.patch("/{booking_id}/change_room")
async def change_room_booking(
    booking_id: UUID,
    payload: ChangeRoomBookingRequest,
    change_room_booking_uc: FromDishka[ChangeRoomBookingUseCase],
    current_user: CurrentUserDep,
) -> BookingResponse:
    booking = await change_room_booking_uc.execute(
        payload.to_dto(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    return BookingResponse.from_dto(booking)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    cancel_booking_uc: FromDishka[CancelBookingUseCase],
    current_user: CurrentUserDep,
) -> BookingResponse:
    booking = await cancel_booking_uc.execute(
        CancelBookingDTO(
            id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    return BookingResponse.from_dto(booking)
