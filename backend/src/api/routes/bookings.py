import logging
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from api.dependencies.auth import AdminUserDep, CurrentUserDep
from api.schemas.bookings import (
    AddBookingParticipantRequest,
    BookingDetailsResponse,
    BookingParticipantResponse,
    BookingResponse,
    ChangeRoomBookingRequest,
    CreateBookingRequest,
    GetAvailableRoomsFilters,
    GetBookingsFilters,
    RescheduleBookingRequest,
)
from api.schemas.rooms import RoomResponse
from usecases.bookings.add_participant import AddBookingParticipantUseCase
from usecases.bookings.cancel_booking import CancelBookingUseCase
from usecases.bookings.change_room import ChangeRoomBookingUseCase
from usecases.bookings.create_booking import CreateBookingUseCase
from usecases.bookings.get_all_bookings import GetAllBookingsUseCase
from usecases.bookings.get_available_rooms import GetAvailableRoomsUseCase
from usecases.bookings.get_booking_details import GetBookingDetailsUseCase
from usecases.bookings.get_my_bookings import GetMyBookingsUseCase
from usecases.bookings.get_room_bookings import GetRoomBookingsUseCase
from usecases.bookings.remove_participant import (
    RemoveBookingParticipantUseCase,
)
from usecases.bookings.reschedule_booking import RescheduleBookingUseCase
from usecases.dto.booking import CancelBookingDTO, RemoveBookingParticipantDTO

router = APIRouter(tags=["bookings"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.bookings")


@router.get("/")
async def get_bookings(
    get_bookings_uc: FromDishka[GetAllBookingsUseCase],
    filters: Annotated[GetBookingsFilters, Query()],
    _: AdminUserDep,
) -> list[BookingResponse]:
    logger.info("get_bookings_started limit=%s offset=%s", filters.limit, filters.offset)
    bookings = await get_bookings_uc.execute(filters.to_dto())
    logger.info("get_bookings_finished count=%s", len(bookings))
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/available-rooms")
async def get_available_rooms(
    get_available_rooms_uc: FromDishka[GetAvailableRoomsUseCase],
    filters: Annotated[GetAvailableRoomsFilters, Query()],
    _: CurrentUserDep,
) -> list[RoomResponse]:
    logger.info("get_available_rooms_started")
    rooms = await get_available_rooms_uc.execute(filters.to_dto())
    logger.info("get_available_rooms_finished count=%s", len(rooms))
    return [RoomResponse.from_dto(room) for room in rooms]


@router.get("/by-room/{room_id}")
async def get_room_bookings(
    room_id: UUID,
    get_room_bookings_uc: FromDishka[GetRoomBookingsUseCase],
    filters: Annotated[GetBookingsFilters, Query()],
    _: CurrentUserDep,
) -> list[BookingResponse]:
    logger.info("get_room_bookings_started room_id=%s", room_id)
    bookings = await get_room_bookings_uc.execute(
        filters.to_dto(room_id=room_id),
    )
    logger.info("get_room_bookings_finished room_id=%s count=%s", room_id, len(bookings))
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/by-user/{user_id}")
async def get_user_bookings(
    user_id: UUID,
    get_user_bookings_uc: FromDishka[GetMyBookingsUseCase],
    filters: Annotated[GetBookingsFilters, Query()],
    _: AdminUserDep,
) -> list[BookingResponse]:
    logger.info("get_user_bookings_started user_id=%s", user_id)
    bookings = await get_user_bookings_uc.execute(
        filters.to_dto(user_id=user_id),
    )
    logger.info("get_user_bookings_finished user_id=%s count=%s", user_id, len(bookings))
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/my-bookings")
async def get_my_bookings(
    get_user_bookings_uc: FromDishka[GetMyBookingsUseCase],
    filters: Annotated[GetBookingsFilters, Query()],
    current_user: CurrentUserDep,
) -> list[BookingResponse]:
    logger.info("get_my_bookings_started user_id=%s", current_user.id)
    bookings = await get_user_bookings_uc.execute(
        filters.to_dto(user_id=current_user.id),
    )
    logger.info("get_my_bookings_finished user_id=%s count=%s", current_user.id, len(bookings))
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/{booking_id}")
async def get_booking(
    booking_id: UUID,
    get_booking_uc: FromDishka[GetBookingDetailsUseCase],
) -> BookingDetailsResponse:
    logger.info("get_booking_started booking_id=%s", booking_id)
    booking = await get_booking_uc.execute(booking_id)
    logger.info("get_booking_finished booking_id=%s", booking.id)
    return BookingDetailsResponse.from_dto(booking)


@router.post("/")
async def create_booking(
    payload: CreateBookingRequest,
    create_booking_uc: FromDishka[CreateBookingUseCase],
    current_user: CurrentUserDep,
) -> BookingResponse:
    logger.info("create_booking_started actor_id=%s room_id=%s", current_user.id, payload.room_id)
    booking = await create_booking_uc.execute(
        payload.to_dto(created_by=current_user.id),
    )
    logger.info("create_booking_finished booking_id=%s", booking.id)
    return BookingResponse.from_dto(booking)


@router.patch("/{booking_id}/reschedule")
async def reschedule_booking(
    booking_id: UUID,
    payload: RescheduleBookingRequest,
    reschedule_booking_uc: FromDishka[RescheduleBookingUseCase],
    current_user: CurrentUserDep,
) -> BookingResponse:
    logger.info("reschedule_booking_started booking_id=%s actor_id=%s", booking_id, current_user.id)
    booking = await reschedule_booking_uc.execute(
        payload.to_dto(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    logger.info("reschedule_booking_finished booking_id=%s", booking.id)
    return BookingResponse.from_dto(booking)


@router.patch("/{booking_id}/change_room")
async def change_room_booking(
    booking_id: UUID,
    payload: ChangeRoomBookingRequest,
    change_room_booking_uc: FromDishka[ChangeRoomBookingUseCase],
    current_user: CurrentUserDep,
) -> BookingResponse:
    logger.info("change_room_booking_started booking_id=%s actor_id=%s", booking_id, current_user.id)
    booking = await change_room_booking_uc.execute(
        payload.to_dto(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    logger.info("change_room_booking_finished booking_id=%s room_id=%s", booking.id, booking.room_id)
    return BookingResponse.from_dto(booking)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    cancel_booking_uc: FromDishka[CancelBookingUseCase],
    current_user: CurrentUserDep,
) -> BookingResponse:
    logger.info("cancel_booking_started booking_id=%s actor_id=%s", booking_id, current_user.id)
    booking = await cancel_booking_uc.execute(
        CancelBookingDTO(
            id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    logger.info("cancel_booking_finished booking_id=%s", booking.id)
    return BookingResponse.from_dto(booking)


@router.post("/{booking_id}/participants")
async def add_booking_participant(
    booking_id: UUID,
    payload: AddBookingParticipantRequest,
    add_booking_participant_uc: FromDishka[AddBookingParticipantUseCase],
    current_user: CurrentUserDep,
) -> BookingParticipantResponse:
    logger.info("add_booking_participant_started booking_id=%s actor_id=%s user_id=%s", booking_id, current_user.id, payload.user_id)
    participant = await add_booking_participant_uc.execute(
        payload.to_dto(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    logger.info("add_booking_participant_finished booking_id=%s user_id=%s", booking_id, participant.user_id)
    return BookingParticipantResponse.from_dto(participant)


@router.delete("/{booking_id}/participants/{user_id}", status_code=204)
async def remove_booking_participant(
    booking_id: UUID,
    user_id: UUID,
    remove_booking_participant_uc: FromDishka[RemoveBookingParticipantUseCase],
    current_user: CurrentUserDep,
) -> None:
    logger.info("remove_booking_participant_started booking_id=%s actor_id=%s user_id=%s", booking_id, current_user.id, user_id)
    await remove_booking_participant_uc.execute(
        RemoveBookingParticipantDTO(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
            user_id=user_id,
        ),
    )
    logger.info("remove_booking_participant_finished booking_id=%s user_id=%s", booking_id, user_id)
