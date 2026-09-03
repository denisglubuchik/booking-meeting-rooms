import logging
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from api.dependencies.auth import AdminUserDep, CurrentUserDep
from api.schemas.users import (
    CreateUserRequest,
    GetUsersFilters,
    UpdateUserRequest,
    UserLookupFilters,
    UserLookupResponse,
    UserResponse,
)
from domain.entities.user import UserRole
from usecases.commands.users.activate_user import (
    ActivateUserCommand,
    ActivateUserCommandHandler,
)
from usecases.commands.users.change_role import (
    ChangeUserRoleCommand,
    ChangeUserRoleCommandHandler,
)
from usecases.commands.users.create_user import CreateUserCommandHandler
from usecases.commands.users.deactivate_user import (
    DeactivateUserCommand,
    DeactivateUserCommandHandler,
)
from usecases.commands.users.update_user import UpdateUserCommandHandler
from usecases.queries.users.get_user_details import (
    GetUserDetailsQuery,
    GetUserDetailsQueryHandler,
)
from usecases.queries.users.get_users import GetUsersQueryHandler
from usecases.queries.users.lookup_users import LookupUsersQueryHandler

router = APIRouter(tags=["Users"], route_class=DishkaRoute)
logger = logging.getLogger("api.routes.users")


@router.get("/")
async def get_users(
    handler: FromDishka[GetUsersQueryHandler],
    filters: Annotated[GetUsersFilters, Query()],
    _: AdminUserDep,
) -> list[UserResponse]:
    logger.info(
        "get_users_started limit=%s offset=%s",
        filters.limit,
        filters.offset,
    )
    users = await handler.handle(filters.to_query())
    logger.info("get_users_finished count=%s", len(users))
    return [UserResponse.from_dto(user) for user in users]


@router.get("/lookup")
async def lookup_users(
    handler: FromDishka[LookupUsersQueryHandler],
    filters: Annotated[UserLookupFilters, Query()],
    _: CurrentUserDep,
) -> list[UserLookupResponse]:
    logger.info("lookup_users_started query=%s", filters.query)
    users = await handler.handle(filters.to_query())
    logger.info("lookup_users_finished count=%s", len(users))
    return [UserLookupResponse.from_dto(user) for user in users]


@router.post("/register")
async def create_user(
    payload: CreateUserRequest,
    handler: FromDishka[CreateUserCommandHandler],
) -> UserResponse:
    logger.info("create_user_started email=%s", payload.email)
    user = await handler.handle(payload.to_command())
    logger.info("create_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.get("/me")
async def get_me(
    handler: FromDishka[GetUserDetailsQueryHandler],
    current_user: CurrentUserDep,
    consistent: bool = False,
) -> UserResponse:
    logger.info(
        "get_me_started user_id=%s consistent=%s",
        current_user.id,
        consistent,
    )
    user = await handler.handle(
        GetUserDetailsQuery(user_id=current_user.id, consistent=consistent),
    )
    logger.info("get_me_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.patch("/me")
async def update_me(
    payload: UpdateUserRequest,
    handler: FromDishka[UpdateUserCommandHandler],
    current_user: CurrentUserDep,
) -> UserResponse:
    logger.info("update_me_started user_id=%s", current_user.id)
    user = await handler.handle(payload.to_command(current_user.id))
    logger.info("update_me_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    handler: FromDishka[GetUserDetailsQueryHandler],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("get_user_started user_id=%s", user_id)
    user = await handler.handle(GetUserDetailsQuery(user_id=user_id))
    logger.info("get_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.patch("/{user_id}")
async def update_user(
    user_id: UUID,
    payload: UpdateUserRequest,
    handler: FromDishka[UpdateUserCommandHandler],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("update_user_started user_id=%s", user_id)
    user = await handler.handle(payload.to_command(user_id))
    logger.info("update_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    handler: FromDishka[ActivateUserCommandHandler],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("activate_user_started user_id=%s", user_id)
    user = await handler.handle(ActivateUserCommand(user_id=user_id))
    logger.info("activate_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    handler: FromDishka[DeactivateUserCommandHandler],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("deactivate_user_started user_id=%s", user_id)
    user = await handler.handle(DeactivateUserCommand(user_id=user_id))
    logger.info("deactivate_user_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/promote-to-admin")
async def promote_to_admin(
    user_id: UUID,
    handler: FromDishka[ChangeUserRoleCommandHandler],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("promote_to_admin_started user_id=%s", user_id)
    user = await handler.handle(
        ChangeUserRoleCommand(user_id=user_id, role=UserRole.ADMIN),
    )
    logger.info("promote_to_admin_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)


@router.post("/{user_id}/demote-to-employee")
async def demote_to_employee(
    user_id: UUID,
    handler: FromDishka[ChangeUserRoleCommandHandler],
    _: AdminUserDep,
) -> UserResponse:
    logger.info("demote_to_employee_started user_id=%s", user_id)
    user = await handler.handle(
        ChangeUserRoleCommand(user_id=user_id, role=UserRole.EMPLOYEE),
    )
    logger.info("demote_to_employee_finished user_id=%s", user.id)
    return UserResponse.from_dto(user)
