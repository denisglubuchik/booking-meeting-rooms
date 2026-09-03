import logging
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, Request, Response

from api.dependencies.auth import CurrentUserDep
from api.schemas.auth import (
    AccessTokenResponse,
    LoginUserRequest,
    UserSessionResponse,
)
from core.config import AuthConfig
from usecases.commands.auth.login import LoginCommandHandler
from usecases.commands.auth.logout import LogoutCommand, LogoutCommandHandler
from usecases.commands.auth.refresh_tokens import (
    RefreshTokensCommand,
    RefreshTokensCommandHandler,
)
from usecases.commands.auth.revoke_user_session import (
    RevokeUserSessionCommand,
    RevokeUserSessionCommandHandler,
)
from usecases.exceptions import UnauthorizedError
from usecases.queries.users.get_user_sessions import (
    GetUserSessionsQuery,
    GetUserSessionsQueryHandler,
)

router = APIRouter(tags=["Auth"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.auth")


@router.post("/login")
async def login(
    payload: LoginUserRequest,
    request: Request,
    response: Response,
    auth_settings: FromDishka[AuthConfig],
    handler: FromDishka[LoginCommandHandler],
) -> AccessTokenResponse:
    logger.info("login_user_started email=%s", payload.email)
    tokens = await handler.handle(
        payload.to_command(
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
        ),
    )
    logger.info("login_user_finished email=%s", payload.email)
    response.set_cookie(
        key=auth_settings.REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=auth_settings.REFRESH_COOKIE_SECURE,
        samesite=auth_settings.REFRESH_COOKIE_SAMESITE,
        path=auth_settings.REFRESH_COOKIE_PATH,
        max_age=auth_settings.JWT_REFRESH_EXPIRES_DAYS * 24 * 60 * 60,
    )
    return AccessTokenResponse(access_token=tokens.access_token)


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    auth_settings: FromDishka[AuthConfig],
    handler: FromDishka[RefreshTokensCommandHandler],
) -> AccessTokenResponse:
    refresh_token = request.cookies.get(auth_settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise UnauthorizedError("Missing refresh token cookie")

    logger.info("refresh_tokens_started")
    tokens = await handler.handle(
        RefreshTokensCommand(
            refresh_token=refresh_token,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
        ),
    )
    logger.info("refresh_tokens_finished")
    response.set_cookie(
        key=auth_settings.REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=auth_settings.REFRESH_COOKIE_SECURE,
        samesite=auth_settings.REFRESH_COOKIE_SAMESITE,
        path=auth_settings.REFRESH_COOKIE_PATH,
        max_age=auth_settings.JWT_REFRESH_EXPIRES_DAYS * 24 * 60 * 60,
    )
    return AccessTokenResponse(access_token=tokens.access_token)


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    auth_settings: FromDishka[AuthConfig],
    handler: FromDishka[LogoutCommandHandler],
) -> None:
    logger.info("logout_started")
    refresh_token = request.cookies.get(auth_settings.REFRESH_COOKIE_NAME)
    if refresh_token:
        await handler.handle(LogoutCommand(refresh_token=refresh_token))
    response.delete_cookie(
        key=auth_settings.REFRESH_COOKIE_NAME,
        path=auth_settings.REFRESH_COOKIE_PATH,
    )
    logger.info("logout_finished")


@router.get("/sessions")
async def get_sessions(
    current_user: CurrentUserDep,
    handler: FromDishka[GetUserSessionsQueryHandler],
    is_active: Annotated[
        bool | None,
        Query(alias="isActive"),
    ] = None,
) -> list[UserSessionResponse]:
    sessions = await handler.handle(
        GetUserSessionsQuery(
            user_id=current_user.id,
            is_active=is_active,
            consistent=True,
        ),
    )
    return [UserSessionResponse.from_dto(session) for session in sessions]


@router.post("/sessions/{session_id}/revoke", status_code=204)
async def revoke_session(
    session_id: UUID,
    current_user: CurrentUserDep,
    handler: FromDishka[RevokeUserSessionCommandHandler],
) -> None:
    await handler.handle(
        RevokeUserSessionCommand(
            user_id=current_user.id,
            session_id=session_id,
        ),
    )
