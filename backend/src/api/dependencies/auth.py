import logging
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from api.schemas.auth import AuthenticatedUser
from domain.entities.user import UserRole
from infra.interfaces.jwt_tokens import (
    JWTTokenServiceInterface,
    JWTTokenVerificationError,
)
from usecases.exceptions import (
    ForbiddenError,
    UnauthorizedError,
)

bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger("api.auth")


@inject
def get_current_user(
    jwt_tokens: FromDishka[JWTTokenServiceInterface],
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme,
    ),
) -> AuthenticatedUser:
    if credentials is None:
        logger.warning("auth_missing_bearer_token")
        raise UnauthorizedError(
            "Missing bearer token",
            code="auth.missing_bearer_token",
        )

    try:
        payload = jwt_tokens.verify_access(credentials.credentials)
    except JWTTokenVerificationError as error:
        logger.warning("auth_invalid_access_token")
        raise UnauthorizedError(
            "Invalid access token",
            code="auth.invalid_access_token",
        ) from error

    try:
        user = AuthenticatedUser(
            id=UUID(str(payload["sub"])),
            email=str(payload["email"]),
            role=UserRole(str(payload["role"])),
            is_active=bool(payload["is_active"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        logger.warning("auth_invalid_token_payload")
        raise UnauthorizedError(
            "Invalid access token",
            code="auth.invalid_access_token",
        ) from error

    if not user.is_active:
        logger.warning("auth_deactivated_user user_id=%s", user.id)
        raise ForbiddenError(
            "User is deactivated",
            code="auth.user_deactivated",
        )

    logger.info(
        "auth_user_resolved user_id=%s role=%s",
        user.id,
        user.role.value,
    )
    return user


def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            "auth_admin_access_denied user_id=%s role=%s",
            current_user.id,
            current_user.role.value,
        )
        raise ForbiddenError(
            "Admin access required",
            code="auth.admin_access_required",
        )
    logger.info("auth_admin_access_granted user_id=%s", current_user.id)
    return current_user


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]
AdminUserDep = Annotated[AuthenticatedUser, Depends(require_admin)]
