from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from usecases.commands.users.create_user import CreateUserCommand
from usecases.commands.users.update_user import UpdateUserCommand
from usecases.dto.user import (
    UserLookupResponseDTO,
    UserResponseDTO,
)
from usecases.queries.users.get_users import GetUsersQuery
from usecases.queries.users.lookup_users import LookupUsersQuery


class GetUsersFilters(BaseModel):
    is_active: bool | None = None
    role: str | None = None
    created_at_gte: datetime | None = None
    created_at_lte: datetime | None = None
    limit: int = 100
    offset: int = 0

    def to_query(self) -> GetUsersQuery:
        return GetUsersQuery(
            is_active=self.is_active,
            role=self.role,
            created_at_gte=self.created_at_gte,
            created_at_lte=self.created_at_lte,
            limit=self.limit,
            offset=self.offset,
        )


class CreateUserRequest(BaseModel):
    full_name: str
    email: str
    password: str

    def to_command(self) -> CreateUserCommand:
        return CreateUserCommand(
            full_name=self.full_name,
            email=self.email,
            password=self.password,
        )


class UpdateUserRequest(BaseModel):
    full_name: str
    email: str

    def to_command(self, user_id: UUID) -> UpdateUserCommand:
        return UpdateUserCommand(
            user_id=user_id,
            full_name=self.full_name,
            email=self.email,
        )


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: UserResponseDTO) -> "UserResponse":
        return cls(
            id=dto.id,
            full_name=dto.full_name,
            email=dto.email,
            role=dto.role,
            is_active=dto.is_active,
            created_at=dto.created_at,
        )


class UserLookupFilters(BaseModel):
    query: str = Field(min_length=2, max_length=255)
    limit: int = Field(default=20, ge=1, le=20)

    def to_query(self) -> LookupUsersQuery:
        return LookupUsersQuery(
            query=self.query,
            limit=self.limit,
        )


class UserLookupResponse(BaseModel):
    id: UUID
    full_name: str
    email: str

    @classmethod
    def from_dto(cls, dto: UserLookupResponseDTO) -> "UserLookupResponse":
        return cls(
            id=dto.id,
            full_name=dto.full_name,
            email=dto.email,
        )
