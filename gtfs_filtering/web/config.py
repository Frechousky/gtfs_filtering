import functools

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Web API settings

    Every setting can be overridden by an environment variable prefixed by 'GTFS_FILTERING_',
    e.g. 'GTFS_FILTERING_MAX_UPLOAD_SIZE_MB=500'
    """

    model_config = SettingsConfigDict(env_prefix="GTFS_FILTERING_", env_file=".env")

    app_name: str = "gtfs-filtering"
    max_upload_size_mb: int = 200
    upload_chunk_size_bytes: int = 1024 * 1024

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()
