from collections.abc import Mapping
from typing import Protocol


class JWTTokenServiceInterface(Protocol):
    def issue_access(
        self,
        subject: str,
        claims: Mapping[str, str | int | bool],
    ) -> str: ...

    def verify_access(self, token: str) -> Mapping[str, str | int | bool]: ...

    def issue_refresh(self, subject: str, session_id: str) -> str: ...

    def verify_refresh(self, token: str) -> Mapping[str, str | int | bool]: ...


class JWTTokenVerificationError(Exception):
    pass
