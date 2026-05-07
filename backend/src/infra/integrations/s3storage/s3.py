import aioboto3
from botocore.client import Config

from core.config import S3Config
from infra.interfaces.file_storage import FileStorageInterface


class S3FileStorage(FileStorageInterface):
    def __init__(self, config: S3Config) -> None:
        self._config = config
        self._session = aioboto3.Session()

    @staticmethod
    def _client_config() -> Config:
        return Config(s3={"addressing_style": "path"})

    def _resolve_client_config(self) -> Config | None:
        if self._config.S3_USE_PATH_STYLE:
            return self._client_config()
        return None

    async def upload(
        self,
        *,
        key: str,
        data: bytes,
        content_type: str,
    ) -> None:
        async with self._session.client(
            "s3",
            region_name=self._config.S3_REGION,
            endpoint_url=self._config.S3_ENDPOINT_URL,
            aws_access_key_id=self._config.S3_ACCESS_KEY_ID,
            aws_secret_access_key=self._config.S3_SECRET_ACCESS_KEY,
            config=self._resolve_client_config(),
        ) as s3:
            await s3.put_object(
                Bucket=self._config.S3_BUCKET,
                Key=key,
                Body=data,
                ContentType=content_type,
            )

    async def generate_presigned_download_url(self, *, key: str) -> str:
        async with self._session.client(
            "s3",
            region_name=self._config.S3_REGION,
            endpoint_url=self._config.S3_ENDPOINT_URL,
            aws_access_key_id=self._config.S3_ACCESS_KEY_ID,
            aws_secret_access_key=self._config.S3_SECRET_ACCESS_KEY,
            config=self._resolve_client_config(),
        ) as s3:
            return await s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self._config.S3_BUCKET,
                    "Key": key,
                },
                ExpiresIn=self._config.S3_PRESIGN_EXPIRES_SECONDS,
            )

    async def delete(self, *, key: str) -> None:
        async with self._session.client(
            "s3",
            region_name=self._config.S3_REGION,
            endpoint_url=self._config.S3_ENDPOINT_URL,
            aws_access_key_id=self._config.S3_ACCESS_KEY_ID,
            aws_secret_access_key=self._config.S3_SECRET_ACCESS_KEY,
            config=self._resolve_client_config(),
        ) as s3:
            await s3.delete_object(Bucket=self._config.S3_BUCKET, Key=key)
