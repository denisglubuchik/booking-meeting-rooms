from collections.abc import Mapping
from typing import Protocol


class AccessTokenIssuerInterface(Protocol):
    def issue(
        self,
        subject: str,
        claims: Mapping[str, str | int | bool],
    ) -> str: ...


class AccessTokenVerifierInterface(Protocol):
    def verify(self, token: str) -> Mapping[str, str | int | bool]: ...


class AccessTokenVerificationError(Exception):
    pass
