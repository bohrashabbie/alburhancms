from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title_en = Column(String(255), nullable=False)
    title_ar = Column(String(255))
    description_en = Column(Text)
    description_ar = Column(Text)
    image_url = Column(String(500))
    icon = Column(String(100))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("ServiceItem", back_populates="service", cascade="all, delete-orphan")


class ServiceItem(Base):
    __tablename__ = "service_items"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    text_en = Column(String(500), nullable=False)
    text_ar = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    service = relationship("Service", back_populates="items")
