from __future__ import annotations

import json
import logging
import logging.config
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, override

from opentelemetry import trace

if TYPE_CHECKING:
    from core.config import LoggingConfig

REQUEST_ID_HEADER = "X-Request-ID"
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def get_request_id() -> str:
    return _request_id_ctx.get()


def set_request_id(request_id: str) -> object:
    return _request_id_ctx.set(request_id)


def reset_request_id(token: object) -> None:
    _request_id_ctx.reset(token)


class RequestIdFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class CorrelationContextFilter(RequestIdFilter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        super().filter(record)

        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            record.trace_id = f"{span_context.trace_id:032x}"
            record.span_id = f"{span_context.span_id:016x}"
        else:
            record.trace_id = "-"
            record.span_id = "-"
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "trace_id": getattr(record, "trace_id", "-"),
            "span_id": getattr(record, "span_id", "-"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def _build_config(*, log_level: str, log_format: str) -> dict[str, object]:
    formatter_name = "json" if log_format == "json" else "console"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_context": {
                "()": CorrelationContextFilter,
            },
        },
        "formatters": {
            "console": {
                "format": (
                    "%(asctime)s %(levelname)s %(name)s "
                    "[request_id=%(request_id)s trace_id=%(trace_id)s "
                    "span_id=%(span_id)s] %(message)s"
                ),
            },
            "json": {
                "()": JsonFormatter,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": formatter_name,
                "filters": ["correlation_context"],
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["default"],
        },
        "loggers": {
            "uvicorn.error": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "api": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "usecases": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "infra": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }


def setup_logging(
    config: LoggingConfig,
    telemetry_handler: logging.Handler | None = None,
) -> None:
    log_level = config.LOG_LEVEL.upper()
    log_format = config.LOG_FORMAT.lower()
    logging.config.dictConfig(
        _build_config(
            log_level=log_level,
            log_format=log_format,
        ),
    )
    if telemetry_handler is not None:
        _attach_telemetry_handler(telemetry_handler, log_level)


def _attach_telemetry_handler(
    handler: logging.Handler,
    log_level: str,
) -> None:
    handler.setLevel(log_level)
    handler.addFilter(RequestIdFilter())
    logging.getLogger().handlers.insert(0, handler)
    for logger_name in (
        "uvicorn.error",
        "uvicorn.access",
        "api",
        "usecases",
        "infra",
    ):
        logging.getLogger(logger_name).handlers.insert(0, handler)
