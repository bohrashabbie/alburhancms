from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"))
    name_en = Column(String(255))
    name_ar = Column(String(255))
    description_en = Column(Text)
    description_ar = Column(Text)
    image_url = Column(String(500))
    banner_type = Column(String(100))
    position = Column(String(100))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
