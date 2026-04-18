import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.media_file import MediaFile
from app.models.user import User

settings = get_settings()


def _safe_folder(value: str) -> str:
    """Normalize a folder hint into a safe relative path."""
    cleaned = value.replace("\\", "/").strip().strip("/")
    parts = [p for p in cleaned.split("/") if p and p not in {".", ".."}]
    return "/".join(parts)


async def save_upload_and_register_media(
    *,
    file: UploadFile,
    db: Session,
    current_user: User,
    folder: str = "",
) -> MediaFile:
    """
    Save an uploaded file to disk and register it in media_files.

    Returns the persisted MediaFile ORM object.
    """
    safe_folder = _safe_folder(folder)
    disk_dir = Path(settings.UPLOAD_DIR)
    if safe_folder:
        disk_dir = disk_dir / safe_folder
    os.makedirs(disk_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    disk_path = disk_dir / unique_name

    content = await file.read()
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
        file_type=file.content_type,
        file_size=len(content),
        uploaded_by=current_user.id,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def delete_media_file_from_disk(media_path: Optional[str]) -> None:
    """Delete a media file from disk if present."""
    if not media_path:
        return
    normalized = media_path.replace("\\", "/")
    if normalized.startswith("/"):
        normalized = normalized[1:]
    disk_path = Path(normalized)
    if disk_path.exists() and disk_path.is_file():
        os.remove(disk_path)
