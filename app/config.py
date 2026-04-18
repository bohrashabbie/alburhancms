from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:Sha2558161@13.60.4.75:5432/alburhancms"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = "*"
    UPLOAD_DIR: str = "uploads"

    # --- Storage backend ---
    # "local" = write files to UPLOAD_DIR on the container filesystem
    # "s3"    = upload files to S3 and return a public URL
    STORAGE_BACKEND: str = "s3"

    # --- AWS / S3 ---
    # Values are loaded from .env at runtime (see .env.example).
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "eu-north-1"
    S3_BUCKET: Optional[str] = None
    # Optional CDN / custom-domain URL to build public links.
    # Leave unset to auto-build: https://{bucket}.s3.{region}.amazonaws.com
    S3_PUBLIC_BASE_URL: Optional[str] = None
    # Extra key prefix inside the bucket (e.g. "cms/"). No leading slash.
    S3_KEY_PREFIX: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
