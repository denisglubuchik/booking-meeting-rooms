from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from domain.time import moscow_now


class UserRole(StrEnum):
    EMPLOYEE = "employee"
    ADMIN = "admin"


@dataclass(slots=True, kw_only=True)
class User:
    id: UUID
    full_name: str
    email: str
    role: UserRole = UserRole.EMPLOYEE
    is_active: bool = True
    created_at: datetime = field(default_factory=moscow_now)

    def promote_to_admin(self) -> None:
        self.role = UserRole.ADMIN

    def demote_to_employee(self) -> None:
        self.role = UserRole.EMPLOYEE
