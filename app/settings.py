from functools import lru_cache
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="./.env", extra="ignore")

    database_url: PostgresDsn

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket_name: str

    cloudfront_domain: str
    cloudfront_key_id: str
    cloudfront_private_key_path: str

    jwt_secret: str
    jwt_access_ttl_minutes: int = 30
    jwt_refresh_ttl_days: int = 30
    google_client_id: str
    redis_url: RedisDsn


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
