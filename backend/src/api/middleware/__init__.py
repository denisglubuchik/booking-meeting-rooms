# ruff: noqa: RUF067
from fastapi import FastAPI

from api.middleware.logging import RequestLoggingMiddleware


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(RequestLoggingMiddleware)
