import logging
from collections.abc import Mapping
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jwt

from core.config import AuthConfig
from infra.interfaces.access_token import (
    AccessTokenIssuerInterface,
    AccessTokenVerificationError,
    AccessTokenVerifierInterface,
)


class JWTAccessTokenIssuer(AccessTokenIssuerInterface):
    def __init__(self, config: AuthConfig) -> None:
        self._secret = config.JWT_ACCESS_SECRET.encode("utf-8")
        self._issuer = config.JWT_ISSUER
        self._ttl = timedelta(minutes=config.JWT_ACCESS_EXPIRES_MINUTES)
        self._logger = logging.getLogger("infra.auth.access_token.issuer")

    def issue(
        self,
        subject: str,
        claims: Mapping[str, str | int | bool],
    ) -> str:
        self._logger.debug(
            "issue_access_token_started subject=%s claims_count=%s",
            subject,
            len(claims),
        )
        now = datetime.now(ZoneInfo("Europe/Moscow"))
        payload = {
            "sub": subject,
            "iss": self._issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + self._ttl).timestamp()),
            **claims,
        }
        token = jwt.encode(payload, self._secret, algorithm="HS256")
        self._logger.debug("issue_access_token_finished subject=%s", subject)
        return token


class JWTAccessTokenVerifier(AccessTokenVerifierInterface):
    def __init__(self, config: AuthConfig) -> None:
        self._secret = config.JWT_ACCESS_SECRET.encode("utf-8")
        self._issuer = config.JWT_ISSUER
        self._logger = logging.getLogger("infra.auth.access_token.verifier")

    def verify(self, token: str) -> Mapping[str, str | int | bool]:
        self._logger.debug("verify_access_token_started")
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                issuer=self._issuer,
                options={"require": ["sub", "iss", "iat", "exp"]},
            )
        except jwt.InvalidTokenError as error:
            self._logger.warning("verify_access_token_failed")
            raise AccessTokenVerificationError from error

        self._logger.debug("verify_access_token_finished")
        return payload
