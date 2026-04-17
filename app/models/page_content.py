from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class PageContent(Base):
    __tablename__ = "page_contents"

    id = Column(Integer, primary_key=True, index=True)
    page_key = Column(String(100), nullable=False, index=True)
    section_key = Column(String(100), nullable=False, index=True)
    title_en = Column(String(500))
    title_ar = Column(String(500))
    content_en = Column(Text)
    content_ar = Column(Text)
    extra_data = Column(JSON, default={})
    image_url = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
