from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class FooterLink(Base):
    __tablename__ = "footer_links"

    id = Column(Integer, primary_key=True, index=True)
    section = Column(String(100), nullable=False)
    label_en = Column(String(255), nullable=False)
    label_ar = Column(String(255))
    href = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
