# ruff: noqa: C901, RUF029
import logging

from fastapi import FastAPI, Request, status
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
    BadRequest,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
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
    @app.exception_handler(NotFoundError)
    async def handle_not_found(
        request: Request,
        exc: NotFoundError,
    ) -> JSONResponse:
        logger.warning("not_found_error path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="not_found",
            message=str(exc),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.exception_handler(ForbiddenError)
    async def handle_forbidden(
        request: Request,
        exc: ForbiddenError,
    ) -> JSONResponse:
        logger.warning("forbidden_error path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="forbidden",
            message=str(exc),
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @app.exception_handler(BadRequest)
    async def handle_bad_request(
        request: Request,
        exc: BadRequest,
    ) -> JSONResponse:
        logger.warning("bad_request_error path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="bad_request",
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(UnauthorizedError)
    async def handle_unauthorized(
        request: Request,
        exc: UnauthorizedError,
    ) -> JSONResponse:
        logger.warning("unauthorized_error path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="invalid_credentials",
            message=str(exc),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @app.exception_handler(BookingTimeInPastError)
    async def handle_booking_time_in_past(
        request: Request,
        exc: BookingTimeInPastError,
    ) -> JSONResponse:
        logger.warning("booking_time_in_past path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="booking_time_in_past",
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(BookingHorizonExceededError)
    async def handle_booking_horizon_exceeded(
        request: Request,
        exc: BookingHorizonExceededError,
    ) -> JSONResponse:
        logger.warning("booking_horizon_exceeded path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="booking_horizon_exceeded",
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(RoomUnavailableError)
    async def handle_room_unavailable(
        request: Request,
        exc: RoomUnavailableError,
    ) -> JSONResponse:
        logger.warning("room_unavailable path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="room_unavailable",
            message=str(exc),
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(InvalidTimeRangeError)
    async def handle_invalid_time_range(
        request: Request,
        exc: InvalidTimeRangeError,
    ) -> JSONResponse:
        logger.warning("invalid_time_range path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="invalid_time_range",
            message=str(exc) or "Invalid time range",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(InvalidBookingStateError)
    async def handle_invalid_booking_state(
        request: Request,
        exc: InvalidBookingStateError,
    ) -> JSONResponse:
        logger.warning(
            "invalid_booking_state path=%s detail=%s",
            request.url.path,
            str(exc),
        )
        return _error_response(
            code="invalid_booking_state",
            message=str(exc) or "Invalid booking state",
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(PermissionDeniedError)
    async def handle_permission_denied(
        request: Request,
        exc: PermissionDeniedError,
    ) -> JSONResponse:
        logger.warning("permission_denied path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="permission_denied",
            message=str(exc) or "Permission denied",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        logger.warning("application_error path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="application_error",
            message=str(exc) or "Application error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        logger.warning("domain_error path=%s detail=%s", request.url.path, str(exc))
        return _error_response(
            code="domain_error",
            message=str(exc) or "Domain error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
