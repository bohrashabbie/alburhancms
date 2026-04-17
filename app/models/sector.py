from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    icon = Column(String(100))
    description_en = Column(Text)
    description_ar = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
