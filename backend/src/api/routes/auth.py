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
from usecases.auth.tokens import (
    GetUserSessionsUseCase,
    LoginWithSessionUseCase,
    LogoutUseCase,
    RefreshTokensUseCase,
    RevokeUserSessionUseCase,
)
from usecases.exceptions import UnauthorizedError
from usecases.user.login_user import LoginUserUseCase

router = APIRouter(tags=["Auth"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.auth")


@router.post("/login")
async def login(
    payload: LoginUserRequest,
    request: Request,
    response: Response,
    auth_settings: FromDishka[AuthConfig],
    login_user_uc: FromDishka[LoginUserUseCase],
    login_with_session_uc: FromDishka[LoginWithSessionUseCase],
) -> AccessTokenResponse:
    logger.info("login_user_started email=%s", payload.email)
    user = await login_user_uc.execute(payload.to_dto())
    tokens = await login_with_session_uc.execute(
        user_id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host if request.client else None,
    )
    logger.info("login_user_finished user_id=%s", user.id)
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
    refresh_uc: FromDishka[RefreshTokensUseCase],
) -> AccessTokenResponse:
    refresh_token = request.cookies.get(auth_settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise UnauthorizedError("Missing refresh token cookie")

    logger.info("refresh_tokens_started")
    tokens = await refresh_uc.execute(
        refresh_token=refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host if request.client else None,
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
    logout_uc: FromDishka[LogoutUseCase],
) -> None:
    logger.info("logout_started")
    refresh_token = request.cookies.get(auth_settings.REFRESH_COOKIE_NAME)
    if refresh_token:
        await logout_uc.execute(refresh_token)
    response.delete_cookie(
        key=auth_settings.REFRESH_COOKIE_NAME,
        path=auth_settings.REFRESH_COOKIE_PATH,
    )
    logger.info("logout_finished")


@router.get("/sessions")
async def get_sessions(
    current_user: CurrentUserDep,
    get_sessions_uc: FromDishka[GetUserSessionsUseCase],
    is_active: Annotated[
        bool | None,
        Query(alias="isActive"),
    ] = None,
) -> list[UserSessionResponse]:
    sessions = await get_sessions_uc.execute(
        current_user.id,
        is_active=is_active,
    )
    return [
        UserSessionResponse(
            id=session.id,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
            created_at=session.created_at,
            user_agent=session.user_agent,
            ip=session.ip,
        )
        for session in sessions
    ]


@router.post("/sessions/{session_id}/revoke", status_code=204)
async def revoke_session(
    session_id: UUID,
    current_user: CurrentUserDep,
    revoke_session_uc: FromDishka[RevokeUserSessionUseCase],
) -> None:
    await revoke_session_uc.execute(current_user.id, session_id)
