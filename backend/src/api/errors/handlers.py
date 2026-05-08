# ruff: noqa: RUF029
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from domain.exceptions import (
    BookingHorizonExceededError,
    BookingTimeInPastError,
    DomainError,
    InvalidBookingStateError,
    InvalidTimeRangeError,
    PermissionDeniedError,
    RoomUnavailableError,
)
from usecases.exceptions import (
    ApplicationError,
)

logger = logging.getLogger("api.errors")


def _error_response(
    *,
    code: str,
    message: str,
    status_code: int,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": message,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "request_validation_error path=%s errors_count=%s",
            request.url.path,
            len(exc.errors()),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "error": {
                    "code": "validation.request_invalid",
                    "message": "Request validation failed",
                },
            },
        )

    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        logger.warning(
            "application_error path=%s detail=%s",
            request.url.path,
            str(exc),
        )
        return _error_response(
            code=exc.code,
            message=str(exc) or "Application error",
            status_code=exc.status_code,
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        logger.warning(
            "domain_error path=%s detail=%s",
            request.url.path,
            str(exc),
        )
        if isinstance(exc, BookingTimeInPastError):
            code = "booking_time_in_past"
            status_code = status.HTTP_400_BAD_REQUEST
            default_message = "Booking time is in the past"
        elif isinstance(exc, BookingHorizonExceededError):
            code = "booking_horizon_exceeded"
            status_code = status.HTTP_400_BAD_REQUEST
            default_message = "Booking horizon exceeded"
        elif isinstance(exc, RoomUnavailableError):
            code = "room_unavailable"
            status_code = status.HTTP_409_CONFLICT
            default_message = "Room unavailable"
        elif isinstance(exc, InvalidTimeRangeError):
            code = "invalid_time_range"
            status_code = status.HTTP_400_BAD_REQUEST
            default_message = "Invalid time range"
        elif isinstance(exc, InvalidBookingStateError):
            code = "invalid_booking_state"
            status_code = status.HTTP_409_CONFLICT
            default_message = "Invalid booking state"
        elif isinstance(exc, PermissionDeniedError):
            code = "permission_denied"
            status_code = status.HTTP_403_FORBIDDEN
            default_message = "Permission denied"
        else:
            code = "domain_error"
            status_code = status.HTTP_400_BAD_REQUEST
            default_message = "Domain error"

        return _error_response(
            code=code,
            message=str(exc) or default_message,
            status_code=status_code,
        )
