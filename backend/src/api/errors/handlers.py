# ruff: noqa: C901, RUF029
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import (
    BookingTimeInPastError,
    DomainError,
    InvalidBookingStateError,
    InvalidTimeRangeError,
    PermissionDeniedError,
    RoomUnavailableError,
)
from usecases.exceptions import (
    ApplicationError,
    BadRequest,
    ForbiddenError,
    NotFoundError,
)


def _error_response(
    *,
    code: str,
    message: str,
    status_code: int,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def handle_not_found(
        _request: Request,
        exc: NotFoundError,
    ) -> JSONResponse:
        return _error_response(
            code="not_found",
            message=str(exc),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.exception_handler(ForbiddenError)
    async def handle_forbidden(
        _request: Request,
        exc: ForbiddenError,
    ) -> JSONResponse:
        return _error_response(
            code="forbidden",
            message=str(exc),
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @app.exception_handler(BadRequest)
    async def handle_bad_request(
        _request: Request,
        exc: BadRequest,
    ) -> JSONResponse:
        return _error_response(
            code="bad_request",
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(BookingTimeInPastError)
    async def handle_booking_time_in_past(
        _request: Request,
        exc: BookingTimeInPastError,
    ) -> JSONResponse:
        return _error_response(
            code="booking_time_in_past",
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(RoomUnavailableError)
    async def handle_room_unavailable(
        _request: Request,
        exc: RoomUnavailableError,
    ) -> JSONResponse:
        return _error_response(
            code="room_unavailable",
            message=str(exc),
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(InvalidTimeRangeError)
    async def handle_invalid_time_range(
        _request: Request,
        exc: InvalidTimeRangeError,
    ) -> JSONResponse:
        return _error_response(
            code="invalid_time_range",
            message=str(exc) or "Invalid time range",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(InvalidBookingStateError)
    async def handle_invalid_booking_state(
        _request: Request,
        exc: InvalidBookingStateError,
    ) -> JSONResponse:
        return _error_response(
            code="invalid_booking_state",
            message=str(exc) or "Invalid booking state",
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(PermissionDeniedError)
    async def handle_permission_denied(
        _request: Request,
        exc: PermissionDeniedError,
    ) -> JSONResponse:
        return _error_response(
            code="permission_denied",
            message=str(exc) or "Permission denied",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        _request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        return _error_response(
            code="application_error",
            message=str(exc) or "Application error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        _request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return _error_response(
            code="domain_error",
            message=str(exc) or "Domain error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
