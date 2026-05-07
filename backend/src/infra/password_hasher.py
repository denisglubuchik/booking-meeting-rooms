import logging

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

from usecases.interfaces.password_hasher import PasswordHasherInterface


class PasswordHasher(PasswordHasherInterface):
    def __init__(self) -> None:
        self._hasher = Argon2Hasher()
        self._logger = logging.getLogger("infra.password_hasher")
        self._logger.debug("password_hasher_initialized")

    def hash(self, password: str) -> str:
        self._logger.debug("password_hash_started")
        hashed = self._hasher.hash(password)
        self._logger.debug("password_hash_finished")
        return hashed

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        self._logger.debug("password_verify_started")
        try:
            result = self._hasher.verify(hashed_password, plain_password)
            self._logger.debug("password_verify_finished result=%s", result)
            return result
        except VerifyMismatchError:
            self._logger.debug("password_verify_finished result=false")
            return False
