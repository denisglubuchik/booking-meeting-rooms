import logging
from collections.abc import Mapping
from datetime import timedelta

import jwt

from core.config import AuthConfig
from domain.time import moscow_now
from infra.interfaces.jwt_tokens import (
    JWTTokenServiceInterface,
    JWTTokenVerificationError,
)


class JWTTokenService(JWTTokenServiceInterface):
    def __init__(self, config: AuthConfig) -> None:
        self._access_secret = config.JWT_ACCESS_SECRET.encode("utf-8")
        self._refresh_secret = config.JWT_REFRESH_SECRET.encode("utf-8")
        self._issuer = config.JWT_ISSUER
        self._access_ttl = timedelta(minutes=config.JWT_ACCESS_EXPIRES_MINUTES)
        self._refresh_ttl = timedelta(days=config.JWT_REFRESH_EXPIRES_DAYS)
        self._logger = logging.getLogger("infra.auth.tokens")

    def issue_access(
        self,
        subject: str,
        claims: Mapping[str, str | int | bool],
    ) -> str:
        now = moscow_now()
        payload = {
            "sub": subject,
            "iss": self._issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + self._access_ttl).timestamp()),
            **claims,
        }
        return jwt.encode(payload, self._access_secret, algorithm="HS256")

    def verify_access(self, token: str) -> Mapping[str, str | int | bool]:
        try:
            return jwt.decode(
                token,
                self._access_secret,
                algorithms=["HS256"],
                issuer=self._issuer,
                options={"require": ["sub", "iss", "iat", "exp"]},
            )
        except jwt.InvalidTokenError as error:
            raise JWTTokenVerificationError from error

    def issue_refresh(self, subject: str, session_id: str) -> str:
        now = moscow_now()
        payload = {
            "sub": subject,
            "sid": session_id,
            "typ": "refresh",
            "iss": self._issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + self._refresh_ttl).timestamp()),
        }
        return jwt.encode(payload, self._refresh_secret, algorithm="HS256")

    def verify_refresh(self, token: str) -> Mapping[str, str | int | bool]:
        try:
            payload = jwt.decode(
                token,
                self._refresh_secret,
                algorithms=["HS256"],
                issuer=self._issuer,
                options={"require": ["sub", "sid", "typ", "iss", "iat", "exp"]},
            )
        except jwt.InvalidTokenError as error:
            raise JWTTokenVerificationError from error

        if payload.get("typ") != "refresh":
            raise JWTTokenVerificationError
        return payload
