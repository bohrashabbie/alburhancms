"""
Media storage utility.

Supports two backends selected via STORAGE_BACKEND env var:
  * "local"  -> writes to ./uploads on the container filesystem
                file_path = "/uploads/<folder>/<uuid>.<ext>"
  * "s3"     -> uploads to S3 using boto3
                file_path = "https://<bucket>.s3.<region>.amazonaws.com/<folder>/<uuid>.<ext>"
                (or your custom S3_PUBLIC_BASE_URL)
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.media_file import MediaFile
from app.models.user import User

settings = get_settings()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_folder(value: str) -> str:
    """Normalize a folder hint into a safe relative path (no leading/trailing
    slash, no traversal)."""
    if not value:
        return ""
    cleaned = value.replace("\\", "/").strip().strip("/")
    parts = [p for p in cleaned.split("/") if p and p not in {".", ".."}]
    return "/".join(parts)


def _build_public_s3_url(key: str) -> str:
    """Build the public URL for an object stored in S3."""
    base = settings.S3_PUBLIC_BASE_URL
    if base:
        return f"{base.rstrip('/')}/{key.lstrip('/')}"
    if not settings.S3_BUCKET:
        raise RuntimeError("S3_BUCKET is not configured")
    return f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key.lstrip('/')}"


def _get_s3_client():
    """Lazily construct a boto3 S3 client so the module still imports when boto3
    isn't installed (e.g. during tests with local backend)."""
    import boto3  # type: ignore

    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def _is_s3() -> bool:
    return (settings.STORAGE_BACKEND or "local").lower() == "s3"


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------

async def save_upload_and_register_media(
    *,
    file: UploadFile,
    db: Session,
    current_user: User,
    folder: str = "",
) -> MediaFile:
    """
    Save an uploaded file to the configured storage backend and register
    a MediaFile row. Returns the persisted ORM object.

    The MediaFile.file_path will be:
      * local: "/uploads/<folder>/<uuid>.<ext>"
      * s3:    "https://<bucket>.s3.<region>.amazonaws.com/<folder>/<uuid>.<ext>"
    """
    safe_folder = _safe_folder(folder)
    ext = os.path.splitext(file.filename or "")[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"

    content = await file.read()
    content_type = file.content_type or "application/octet-stream"

    if _is_s3():
        if not settings.S3_BUCKET:
            raise HTTPException(
                status_code=500,
                detail="Server misconfigured: STORAGE_BACKEND=s3 but S3_BUCKET is not set",
            )

        key_parts = []
        if settings.S3_KEY_PREFIX:
            key_parts.append(settings.S3_KEY_PREFIX.strip("/"))
        if safe_folder:
            key_parts.append(safe_folder)
        key_parts.append(unique_name)
        key = "/".join(p for p in key_parts if p)

        try:
            s3 = _get_s3_client()
            s3.put_object(
                Bucket=settings.S3_BUCKET,
                Key=key,
                Body=content,
                ContentType=content_type,
            )
        except Exception as e:  # pragma: no cover
            raise HTTPException(status_code=500, detail=f"S3 upload failed: {e}")

        public_path = _build_public_s3_url(key)
    else:
        disk_dir = Path(settings.UPLOAD_DIR)
        if safe_folder:
            disk_dir = disk_dir / safe_folder
        os.makedirs(disk_dir, exist_ok=True)

        disk_path = disk_dir / unique_name
        with open(disk_path, "wb") as f:
            f.write(content)

        rel_parts = [settings.UPLOAD_DIR]
        if safe_folder:
            rel_parts.append(safe_folder)
        rel_parts.append(unique_name)
        public_path = "/" + "/".join(rel_parts).replace("\\", "/")

    media = MediaFile(
        filename=unique_name,
        original_name=file.filename,
        file_path=public_path,
        file_type=content_type,
        file_size=len(content),
        uploaded_by=current_user.id,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def delete_media_file_from_disk(media_path: Optional[str]) -> None:
    """
    Delete the backing file for a MediaFile row.

    Handles both legacy local paths ("/uploads/...") and S3 URLs
    ("https://bucket.s3..."). Function name kept for backwards
    compatibility with existing callers.
    """
    if not media_path:
        return

    # S3-hosted object (full URL)
    if media_path.startswith(("http://", "https://")):
        if not _is_s3() or not settings.S3_BUCKET:
            return
        parsed = urlparse(media_path)
        host = parsed.netloc
        key = parsed.path.lstrip("/")
        if not key:
            return

        # If a CDN / custom domain is used, we can't always tell the bucket
        # from the host, so fall back to S3_BUCKET + stripping the key prefix.
        if settings.S3_PUBLIC_BASE_URL:
            base_parsed = urlparse(settings.S3_PUBLIC_BASE_URL)
            base_path = base_parsed.path.strip("/")
            if base_path and key.startswith(base_path + "/"):
                key = key[len(base_path) + 1 :]
            bucket = settings.S3_BUCKET
        else:
            # Host is "<bucket>.s3.<region>.amazonaws.com"
            bucket = host.split(".")[0] if "." in host else settings.S3_BUCKET

        try:
            s3 = _get_s3_client()
            s3.delete_object(Bucket=bucket, Key=key)
        except Exception:
            # Don't let S3 failures block DB deletes.
            pass
        return

    # Local file
    normalized = media_path.replace("\\", "/")
    if normalized.startswith("/"):
        normalized = normalized[1:]
    disk_path = Path(normalized)
    if disk_path.exists() and disk_path.is_file():
        try:
            os.remove(disk_path)
        except OSError:
            pass
