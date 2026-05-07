import logging
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
logger = logging.getLogger("api.routes.users")


@router.get("/")
async def get_users(
    get_users_uc: FromDishka[GetUsersUseCase],
    filters: Annotated[GetUsersFilters, Query()],
    _: AdminUserDep,
) -> list[UserResponse]:
    logger.info("get_users_started limit=%s offset=%s", filters.limit, filters.offset)
    users = await get_users_uc.execute(filters.to_dto())
    logger.info("get_users_finished count=%s", len(users))
    return [UserResponse.from_dto(user) for user in users]


@router.get("/lookup")
async def lookup_users(
    lookup_users_uc: FromDishka[LookupUsersUseCase],
    filters: Annotated[UserLookupFilters, Query()],
    _: CurrentUserDep,
) -> list[UserLookupResponse]:
    logger.info("lookup_users_started query=%s", filters.query)
    users = await lookup_users_uc.execute(filters.to_dto())
    logger.info("lookup_users_finished count=%s", len(users))
    return [UserLookupResponse.from_dto(user) for user in users]


@router.post("/register")
async def create_user(
    payload: CreateUserRequest,
    create_user_uc: FromDishka[CreateUserUseCase],
) -> UserResponse:
    logger.info("create_user_started email=%s", payload.email)
    user = await create_user_uc.execute(payload.to_dto())
    logger.info("create_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/login")
async def login_user(
    payload: LoginUserRequest,
    login_user_uc: FromDishka[LoginUserUseCase],
    token_issuer: FromDishka[AccessTokenIssuerInterface],
) -> AccessTokenResponse:
    logger.info("login_user_started email=%s", payload.email)
    user = await login_user_uc.execute(payload.to_dto())
    token = token_issuer.issue(
        subject=str(user.id),
        claims={
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        },
    )
    logger.info("login_user_finished user_id=%s", user.id)
    return AccessTokenResponse(access_token=token)


@router.get("/me")
async def get_me(
    get_user_uc: FromDishka[GetUserDetailsUseCase],
    current_user: CurrentUserDep,
) -> UserResponse:
    logger.info("get_me_started user_id=%s", current_user.id)
    user = await get_user_uc.execute(current_user.id)
    logger.info("get_me_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.patch("/me")
async def update_me(
    payload: UpdateUserRequest,
    update_user_uc: FromDishka[UpdateUserUseCase],
    current_user: CurrentUserDep,
) -> UserResponse:
    logger.info("update_me_started user_id=%s", current_user.id)
    user = await update_user_uc.execute(payload.to_dto(current_user.id))
    logger.info("update_me_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    get_user_uc: FromDishka[GetUserDetailsUseCase],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("get_user_started user_id=%s", user_id)
    user = await get_user_uc.execute(user_id)
    logger.info("get_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.patch("/{user_id}")
async def update_user(
    user_id: UUID,
    payload: UpdateUserRequest,
    update_user_uc: FromDishka[UpdateUserUseCase],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("update_user_started user_id=%s", user_id)
    user = await update_user_uc.execute(payload.to_dto(user_id))
    logger.info("update_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    activate_user_uc: FromDishka[ActivateUserUseCase],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("activate_user_started user_id=%s", user_id)
    user = await activate_user_uc.execute(user_id)
    logger.info("activate_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    deactivate_user_uc: FromDishka[DeactivateUserUseCase],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("deactivate_user_started user_id=%s", user_id)
    user = await deactivate_user_uc.execute(user_id)
    logger.info("deactivate_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/promote-to-admin")
async def promote_to_admin(
    user_id: UUID,
    change_role_uc: FromDishka[ChangeUserRoleUseCase],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("promote_to_admin_started user_id=%s", user_id)
    user = await change_role_uc.promote_to_admin(user_id)
    logger.info("promote_to_admin_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/demote-to-employee")
async def demote_to_employee(
    user_id: UUID,
    change_role_uc: FromDishka[ChangeUserRoleUseCase],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("demote_to_employee_started user_id=%s", user_id)
    user = await change_role_uc.demote_to_employee(user_id)
    logger.info("demote_to_employee_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)
