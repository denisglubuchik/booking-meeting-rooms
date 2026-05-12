from typing import Protocol


class HasherInterface(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, plain_password: str, hashed_password: str) -> bool: ...
