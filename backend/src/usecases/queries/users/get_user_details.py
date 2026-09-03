import logging
from dataclasses import dataclass
from uuid import UUID

from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.queries import (
    ConsistentUsersQueryInterface,
    UsersQueryInterface,
)


@dataclass(frozen=True, slots=True)
class GetUserDetailsQuery:
    user_id: UUID
    consistent: bool = False


class GetUserDetailsQueryHandler:
    def __init__(
        self,
        user_repo: UsersQueryInterface,
        consistent_user_repo: ConsistentUsersQueryInterface,
    ) -> None:
        self.user_repo = user_repo
        self.consistent_user_repo = consistent_user_repo
        self.logger = logging.getLogger(
            "usecases.queries.users.get_user_details",
        )

    async def handle(self, query: GetUserDetailsQuery) -> UserResponseDTO:
        self.logger.debug(
            "get_user_details_query_started user_id=%s",
            query.user_id,
        )
        repository = (
            self.consistent_user_repo if query.consistent else self.user_repo
        )
        async with repository:
            user = await repository.get_by_id(query.user_id)
            if not user:
                self.logger.warning(
                    "get_user_details_not_found user_id=%s",
                    query.user_id,
                )
                raise NotFoundError(
                    f"User with id={query.user_id} not found",
                )
            self.logger.debug(
                "get_user_details_query_finished user_id=%s",
                user.id,
            )

            return UserResponseDTO(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
            )
