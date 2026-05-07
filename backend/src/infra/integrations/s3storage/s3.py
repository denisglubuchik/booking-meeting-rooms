import aioboto3
from botocore.client import Config

from core.config import S3Config
from infra.interfaces.cache import CacheInterface
from infra.interfaces.file_storage import FileStorageInterface


class S3FileStorage(FileStorageInterface):
    _PRESIGNED_URL_CACHE_PREFIX = "s3:presign"
    _CACHE_CONTROL_VALUE = "public, max-age=31536000, immutable"

    def __init__(
        self,
        config: S3Config,
        cache: CacheInterface | None = None,
    ) -> None:
        self._config = config
        self._cache = cache
        self._session = aioboto3.Session()

    @staticmethod
    def _client_config() -> Config:
        return Config(s3={"addressing_style": "path"})

    def _resolve_client_config(self) -> Config | None:
        if self._config.S3_USE_PATH_STYLE:
            return self._client_config()
        return None

    def _presigned_url_cache_key(self, key: str) -> str:
        return f"{self._PRESIGNED_URL_CACHE_PREFIX}:{key}"

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
                CacheControl=self._CACHE_CONTROL_VALUE,
            )

    async def generate_presigned_download_url(self, *, key: str) -> str:
        cache_key = self._presigned_url_cache_key(key)
        if self._cache is not None:
            cached_url = await self._cache.get(cache_key, str)
            if cached_url:
                return cached_url

        async with self._session.client(
            "s3",
            region_name=self._config.S3_REGION,
            endpoint_url=self._config.S3_ENDPOINT_URL,
            aws_access_key_id=self._config.S3_ACCESS_KEY_ID,
            aws_secret_access_key=self._config.S3_SECRET_ACCESS_KEY,
            config=self._resolve_client_config(),
        ) as s3:
            presigned_url = await s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self._config.S3_BUCKET,
                    "Key": key,
                },
                ExpiresIn=self._config.S3_PRESIGN_EXPIRES_SECONDS,
            )
            if self._cache is not None:
                await self._cache.set(
                    cache_key,
                    presigned_url,
                    ttl=self._config.S3_PRESIGN_EXPIRES_SECONDS - 60,
                )
            return presigned_url

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
        if self._cache is not None:
            await self._cache.delete(self._presigned_url_cache_key(key))
