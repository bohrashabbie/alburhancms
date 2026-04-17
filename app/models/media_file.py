from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    original_name = Column(String(500))
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100))
    file_size = Column(Integer)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
