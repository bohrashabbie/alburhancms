from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.media_file import MediaFile
from app.models.user import User
from app.schemas.schemas import MediaFileOut
from app.utils.auth import get_current_user
from app.utils.cache import invalidates_cache
from app.utils.media import save_upload_and_register_media, delete_media_file_from_disk

router = APIRouter(prefix="/api/media", tags=["Media"])


@router.post("/upload", response_model=MediaFileOut)
@invalidates_cache
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await save_upload_and_register_media(
        file=file,
        db=db,
        current_user=current_user,
        folder=folder or "media",
    )


@router.get("", response_model=List[MediaFileOut])
def list_media(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MediaFile).order_by(MediaFile.created_at.desc()).all()


@router.delete("/{media_id}")
@invalidates_cache
def delete_media(media_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    media = db.query(MediaFile).filter(MediaFile.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    delete_media_file_from_disk(media.file_path)
    db.delete(media)
    db.commit()
    return {"detail": "Media deleted"}
