from typing import Protocol


class FileStorageInterface(Protocol):
    async def upload(
        self,
        *,
        key: str,
        data: bytes,
        content_type: str,
    ) -> None: ...

    async def generate_presigned_download_url(self, *, key: str) -> str: ...

    async def delete(self, *, key: str) -> None: ...
