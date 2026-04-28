from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from api.schemas.users import AuthenticatedUser
from domain.entities.user import UserRole
from infra.interfaces.access_token import (
    AccessTokenVerificationError,
    AccessTokenVerifierInterface,
)

bearer_scheme = HTTPBearer(auto_error=False)


@inject
def get_current_user(
    token_verifier: FromDishka[AccessTokenVerifierInterface],
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme,
    ),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    try:
        payload = token_verifier.verify(credentials.credentials)
    except AccessTokenVerificationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from error

    try:
        user = AuthenticatedUser(
            id=UUID(str(payload["sub"])),
            email=str(payload["email"]),
            role=UserRole(str(payload["role"])),
            is_active=bool(payload["is_active"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from error

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is deactivated",
        )

    return user


def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]
AdminUserDep = Annotated[AuthenticatedUser, Depends(require_admin)]
