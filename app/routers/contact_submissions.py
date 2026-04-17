from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contact_submission import ContactSubmission
from app.models.user import User
from app.schemas.schemas import ContactSubmissionOut
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/contact-submissions", tags=["Contact Submissions"])


@router.get("", response_model=List[ContactSubmissionOut])
def list_submissions(
    is_read: bool = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ContactSubmission)
    if is_read is not None:
        q = q.filter(ContactSubmission.is_read == is_read)
    return q.order_by(ContactSubmission.created_at.desc()).all()


@router.get("/{submission_id}", response_model=ContactSubmissionOut)
def get_submission(submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = db.query(ContactSubmission).filter(ContactSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub


@router.put("/{submission_id}/read")
def mark_as_read(submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = db.query(ContactSubmission).filter(ContactSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    sub.is_read = True
    db.commit()
    return {"detail": "Marked as read"}


@router.delete("/{submission_id}")
def delete_submission(submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = db.query(ContactSubmission).filter(ContactSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    db.delete(sub)
    db.commit()
    return {"detail": "Submission deleted"}
