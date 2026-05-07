from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from api.dependencies.auth import AdminUserDep, CurrentUserDep
from api.schemas.users import (
    AccessTokenResponse,
    CreateUserRequest,
    GetUsersFilters,
    LoginUserRequest,
    UpdateUserRequest,
    UserLookupFilters,
    UserLookupResponse,
    UserResponse,
)
from infra.interfaces.access_token import AccessTokenIssuerInterface
from usecases.user.activate_user import ActivateUserUseCase
from usecases.user.change_role import ChangeUserRoleUseCase
from usecases.user.create_user import CreateUserUseCase
from usecases.user.deactivate_user import DeactivateUserUseCase
from usecases.user.get_user_details import GetUserDetailsUseCase
from usecases.user.get_users import GetUsersUseCase
from usecases.user.login_user import LoginUserUseCase
from usecases.user.lookup_users import LookupUsersUseCase
from usecases.user.update_user import UpdateUserUseCase

router = APIRouter(tags=["Users"], route_class=DishkaRoute)


@router.get("/")
async def get_users(
    get_users_uc: FromDishka[GetUsersUseCase],
    filters: Annotated[GetUsersFilters, Query()],
    _: AdminUserDep,
) -> list[UserResponse]:
    users = await get_users_uc.execute(filters.to_dto())
    return [UserResponse.from_dto(user) for user in users]


@router.get("/lookup")
async def lookup_users(
    lookup_users_uc: FromDishka[LookupUsersUseCase],
    filters: Annotated[UserLookupFilters, Query()],
    _: CurrentUserDep,
) -> list[UserLookupResponse]:
    users = await lookup_users_uc.execute(filters.to_dto())
    return [UserLookupResponse.from_dto(user) for user in users]


@router.post("/register")
async def create_user(
    payload: CreateUserRequest,
    create_user_uc: FromDishka[CreateUserUseCase],
) -> UserResponse:
    user = await create_user_uc.execute(payload.to_dto())
    return UserResponse.from_dto(user)


@router.post("/login")
async def login_user(
    payload: LoginUserRequest,
    login_user_uc: FromDishka[LoginUserUseCase],
    token_issuer: FromDishka[AccessTokenIssuerInterface],
) -> AccessTokenResponse:
    user = await login_user_uc.execute(payload.to_dto())
    token = token_issuer.issue(
        subject=str(user.id),
        claims={
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        },
    )
    return AccessTokenResponse(access_token=token)


@router.get("/me")
async def get_me(
    get_user_uc: FromDishka[GetUserDetailsUseCase],
    current_user: CurrentUserDep,
) -> UserResponse:
    user = await get_user_uc.execute(current_user.id)
    return UserResponse.from_dto(user)


@router.patch("/me")
async def update_me(
    payload: UpdateUserRequest,
    update_user_uc: FromDishka[UpdateUserUseCase],
    current_user: CurrentUserDep,
) -> UserResponse:
    user = await update_user_uc.execute(payload.to_dto(current_user.id))
    return UserResponse.from_dto(user)


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    get_user_uc: FromDishka[GetUserDetailsUseCase],
    _: AdminUserDep,
) -> UserResponse:
    user = await get_user_uc.execute(user_id)
    return UserResponse.from_dto(user)


@router.patch("/{user_id}")
async def update_user(
    user_id: UUID,
    payload: UpdateUserRequest,
    update_user_uc: FromDishka[UpdateUserUseCase],
    _: AdminUserDep,
) -> UserResponse:
    user = await update_user_uc.execute(payload.to_dto(user_id))
    return UserResponse.from_dto(user)


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    activate_user_uc: FromDishka[ActivateUserUseCase],
    _: AdminUserDep,
) -> UserResponse:
    user = await activate_user_uc.execute(user_id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    deactivate_user_uc: FromDishka[DeactivateUserUseCase],
    _: AdminUserDep,
) -> UserResponse:
    user = await deactivate_user_uc.execute(user_id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/promote-to-admin")
async def promote_to_admin(
    user_id: UUID,
    change_role_uc: FromDishka[ChangeUserRoleUseCase],
    _: AdminUserDep,
) -> UserResponse:
    user = await change_role_uc.promote_to_admin(user_id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/demote-to-employee")
async def demote_to_employee(
    user_id: UUID,
    change_role_uc: FromDishka[ChangeUserRoleUseCase],
    _: AdminUserDep,
) -> UserResponse:
    user = await change_role_uc.demote_to_employee(user_id)
    return UserResponse.from_dto(user)
