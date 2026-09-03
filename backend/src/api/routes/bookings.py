import logging
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from api.dependencies.auth import AdminUserDep, CurrentUserDep
from api.schemas.bookings import (
    AddBookingParticipantRequest,
    AddBookingParticipantResponse,
    BookingDetailsResponse,
    BookingHistoryResponse,
    BookingResponse,
    ChangeRoomBookingRequest,
    CreateBookingRequest,
    GetAvailableRoomsFilters,
    GetBookingHistoryFilters,
    GetBookingsFilters,
    RescheduleBookingRequest,
)
from api.schemas.rooms import RoomResponse
from usecases.commands.bookings.add_participant import (
    AddBookingParticipantCommandHandler,
)
from usecases.commands.bookings.cancel_booking import (
    CancelBookingCommand,
    CancelBookingCommandHandler,
)
from usecases.commands.bookings.change_room import (
    ChangeRoomBookingCommandHandler,
)
from usecases.commands.bookings.create_booking import (
    CreateBookingCommandHandler,
)
from usecases.commands.bookings.remove_participant import (
    RemoveBookingParticipantCommand,
    RemoveBookingParticipantCommandHandler,
)
from usecases.commands.bookings.reschedule_booking import (
    RescheduleBookingCommandHandler,
)
from usecases.queries.bookings.get_all_bookings import (
    GetAllBookingsQueryHandler,
)
from usecases.queries.bookings.get_available_rooms import (
    GetAvailableRoomsQueryHandler,
)
from usecases.queries.bookings.get_booking_details import (
    GetBookingDetailsQuery,
    GetBookingDetailsQueryHandler,
)
from usecases.queries.bookings.get_booking_history import (
    GetBookingHistoryQueryHandler,
)
from usecases.queries.bookings.get_room_bookings import (
    GetRoomBookingsQueryHandler,
)
from usecases.queries.bookings.get_user_bookings import (
    GetUserBookingsQueryHandler,
)

router = APIRouter(tags=["bookings"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.bookings")


@router.get("/")
async def get_bookings(
    handler: FromDishka[GetAllBookingsQueryHandler],
    filters: Annotated[GetBookingsFilters, Query()],
    _: AdminUserDep,
) -> list[BookingResponse]:
    logger.info(
        "get_bookings_started limit=%s offset=%s",
        filters.limit,
        filters.offset,
    )
    bookings = await handler.handle(filters.to_all_query())
    logger.info("get_bookings_finished count=%s", len(bookings))
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/history")
async def get_booking_history(
    handler: FromDishka[GetBookingHistoryQueryHandler],
    filters: Annotated[GetBookingHistoryFilters, Query()],
    _: AdminUserDep,
) -> list[BookingHistoryResponse]:
    logger.info(
        "get_booking_history_started limit=%s offset=%s",
        filters.limit,
        filters.offset,
    )
    history = await handler.handle(filters.to_query())
    logger.info("get_booking_history_finished count=%s", len(history))
    return [BookingHistoryResponse.from_dto(item) for item in history]


@router.get("/available-rooms")
async def get_available_rooms(
    handler: FromDishka[GetAvailableRoomsQueryHandler],
    filters: Annotated[GetAvailableRoomsFilters, Query()],
    _: CurrentUserDep,
) -> list[RoomResponse]:
    logger.info("get_available_rooms_started")
    rooms = await handler.handle(filters.to_query())
    logger.info("get_available_rooms_finished count=%s", len(rooms))
    return [RoomResponse.from_dto(room) for room in rooms]


@router.get("/by-room/{room_id}")
async def get_room_bookings(
    room_id: UUID,
    handler: FromDishka[GetRoomBookingsQueryHandler],
    filters: Annotated[GetBookingsFilters, Query()],
    _: CurrentUserDep,
) -> list[BookingResponse]:
    logger.info("get_room_bookings_started room_id=%s", room_id)
    bookings = await handler.handle(filters.to_room_query(room_id=room_id))
    logger.info(
        "get_room_bookings_finished room_id=%s count=%s",
        room_id,
        len(bookings),
    )
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/by-user/{user_id}")
async def get_user_bookings(
    user_id: UUID,
    handler: FromDishka[GetUserBookingsQueryHandler],
    filters: Annotated[GetBookingsFilters, Query()],
    _: AdminUserDep,
) -> list[BookingResponse]:
    logger.info("get_user_bookings_started user_id=%s", user_id)
    bookings = await handler.handle(filters.to_user_query(user_id=user_id))
    logger.info(
        "get_user_bookings_finished user_id=%s count=%s",
        user_id,
        len(bookings),
    )
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/my-bookings")
async def get_my_bookings(
    handler: FromDishka[GetUserBookingsQueryHandler],
    filters: Annotated[GetBookingsFilters, Query()],
    current_user: CurrentUserDep,
) -> list[BookingResponse]:
    logger.info("get_my_bookings_started user_id=%s", current_user.id)
    bookings = await handler.handle(
        filters.to_user_query(user_id=current_user.id),
    )
    logger.info(
        "get_my_bookings_finished user_id=%s count=%s",
        current_user.id,
        len(bookings),
    )
    return [BookingResponse.from_dto(booking) for booking in bookings]


@router.get("/{booking_id}")
async def get_booking(
    booking_id: UUID,
    handler: FromDishka[GetBookingDetailsQueryHandler],
    _: CurrentUserDep,
    consistent: bool = False,
) -> BookingDetailsResponse:
    logger.info("get_booking_started booking_id=%s", booking_id)
    booking = await handler.handle(
        GetBookingDetailsQuery(
            booking_id=booking_id,
            consistent=consistent,
        ),
    )
    logger.info("get_booking_finished booking_id=%s", booking_id)
    return BookingDetailsResponse.from_dto(booking)


@router.post("/")
async def create_booking(
    payload: CreateBookingRequest,
    handler: FromDishka[CreateBookingCommandHandler],
    current_user: CurrentUserDep,
) -> BookingResponse:
    logger.info(
        "create_booking_started actor_id=%s room_id=%s",
        current_user.id,
        payload.room_id,
    )
    booking = await handler.handle(
        payload.to_command(created_by=current_user.id),
    )
    logger.info("create_booking_finished booking_id=%s", booking.id)
    return BookingResponse.from_dto(booking)


@router.patch("/{booking_id}/reschedule")
async def reschedule_booking(
    booking_id: UUID,
    payload: RescheduleBookingRequest,
    handler: FromDishka[RescheduleBookingCommandHandler],
    current_user: CurrentUserDep,
) -> BookingResponse:
    logger.info(
        "reschedule_booking_started booking_id=%s actor_id=%s",
        booking_id,
        current_user.id,
    )
    booking = await handler.handle(
        payload.to_command(
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
    handler: FromDishka[ChangeRoomBookingCommandHandler],
    current_user: CurrentUserDep,
) -> BookingResponse:
    logger.info(
        "change_room_booking_started booking_id=%s actor_id=%s",
        booking_id,
        current_user.id,
    )
    booking = await handler.handle(
        payload.to_command(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    logger.info(
        "change_room_booking_finished booking_id=%s room_id=%s",
        booking.id,
        booking.room_id,
    )
    return BookingResponse.from_dto(booking)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    handler: FromDishka[CancelBookingCommandHandler],
    current_user: CurrentUserDep,
) -> BookingResponse:
    logger.info(
        "cancel_booking_started booking_id=%s actor_id=%s",
        booking_id,
        current_user.id,
    )
    booking = await handler.handle(
        CancelBookingCommand(
            booking_id=booking_id,
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
    handler: FromDishka[AddBookingParticipantCommandHandler],
    current_user: CurrentUserDep,
) -> AddBookingParticipantResponse:
    logger.info(
        "add_booking_participant_started booking_id=%s actor_id=%s user_id=%s",
        booking_id,
        current_user.id,
        payload.user_id,
    )
    participant = await handler.handle(
        payload.to_command(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
        ),
    )
    logger.info(
        "add_booking_participant_finished booking_id=%s user_id=%s",
        booking_id,
        participant.participant.user_id,
    )
    return AddBookingParticipantResponse.from_dto(participant)


@router.delete("/{booking_id}/participants/{user_id}", status_code=204)
async def remove_booking_participant(
    booking_id: UUID,
    user_id: UUID,
    handler: FromDishka[RemoveBookingParticipantCommandHandler],
    current_user: CurrentUserDep,
) -> None:
    logger.info(
        "remove_booking_participant_started "
        "booking_id=%s actor_id=%s user_id=%s",
        booking_id,
        current_user.id,
        user_id,
    )
    await handler.handle(
        RemoveBookingParticipantCommand(
            booking_id=booking_id,
            actor_id=current_user.id,
            actor_role=current_user.role,
            user_id=user_id,
        ),
    )
    logger.info(
        "remove_booking_participant_finished booking_id=%s user_id=%s",
        booking_id,
        user_id,
    )
