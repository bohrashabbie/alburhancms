from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    slug = Column(String(100), unique=True, nullable=False)
    firm_name_en = Column(String(255))
    firm_name_ar = Column(String(255))
    description_en = Column(Text)
    description_ar = Column(Text)
    flag_url = Column(String(500))
    country_image_url = Column(String(500))
    logo_url = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    branches = relationship("Branch", back_populates="country", cascade="all, delete-orphan")
    contact_infos = relationship("ContactInfo", back_populates="country")
    projects = relationship("Project", back_populates="country")
