import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.media_file import MediaFile
from app.models.user import User
from app.schemas.schemas import MediaFileOut
from app.utils.auth import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/api/media", tags=["Media"])
settings = get_settings()


@router.post("/upload", response_model=MediaFileOut)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    media = MediaFile(
        filename=unique_name,
        original_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        uploaded_by=current_user.id,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


@router.get("", response_model=List[MediaFileOut])
def list_media(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MediaFile).order_by(MediaFile.created_at.desc()).all()


@router.delete("/{media_id}")
def delete_media(media_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    media = db.query(MediaFile).filter(MediaFile.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if os.path.exists(media.file_path):
        os.remove(media.file_path)
    db.delete(media)
    db.commit()
    return {"detail": "Media deleted"}
