import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import override

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.logging import (
    REQUEST_ID_HEADER,
    reset_request_id,
    set_request_id,
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    @override
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        token = set_request_id(request_id)
        started = time.perf_counter()
        logger = logging.getLogger("api.http")

        logger.info(
            "request_started method=%s path=%s",
            request.method,
            request.url.path,
        )
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            logger.exception(
                "request_failed method=%s path=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise
        else:
            duration_ms = (time.perf_counter() - started) * 1000
            response.headers[REQUEST_ID_HEADER] = request_id
            logger.info(
                "request_finished method=%s path=%s status_code=%s "
                "duration_ms=%.2f",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
            return response
        finally:
            reset_request_id(token)
