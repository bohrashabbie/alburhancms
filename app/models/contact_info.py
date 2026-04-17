from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ContactInfo(Base):
    __tablename__ = "contact_info"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"))
    company_name_en = Column(String(255))
    company_name_ar = Column(String(255))
    office_en = Column(String(255))
    office_ar = Column(String(255))
    floor_en = Column(String(255))
    floor_ar = Column(String(255))
    area_en = Column(String(255))
    area_ar = Column(String(255))
    city_en = Column(String(255))
    city_ar = Column(String(255))
    address_en = Column(Text)
    address_ar = Column(Text)
    district_en = Column(String(255))
    district_ar = Column(String(255))
    province_en = Column(String(255))
    province_ar = Column(String(255))
    postal_code = Column(String(50))
    phone1 = Column(String(50))
    phone2 = Column(String(50))
    email = Column(String(255))
    website = Column(String(255))
    business_hours_en = Column(String(255))
    business_hours_ar = Column(String(255))
    is_head_office = Column(Boolean, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="contact_infos")
