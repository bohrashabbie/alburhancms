from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    subject = Column(String(500))
    message = Column(Text)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
