from dataclasses import dataclass


@dataclass(frozen=True)
class AuthTokensDTO:
    access_token: str
    refresh_token: str
