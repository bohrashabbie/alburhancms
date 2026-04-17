from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    name_en = Column(String(255))
    name_ar = Column(String(255))
    address_en = Column(Text)
    address_ar = Column(Text)
    phone1 = Column(String(50))
    phone2 = Column(String(50))
    email = Column(String(255))
    map_lat = Column(Numeric(10, 8))
    map_lng = Column(Numeric(11, 8))
    is_head_office = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="branches")
