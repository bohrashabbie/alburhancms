from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class CarouselSlide(Base):
    __tablename__ = "carousel_slides"

    id = Column(Integer, primary_key=True, index=True)
    title_en = Column(String(255))
    title_ar = Column(String(255))
    subtitle_en = Column(String(255))
    subtitle_ar = Column(String(255))
    description_en = Column(Text)
    description_ar = Column(Text)
    image_url = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
