from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class NavigationItem(Base):
    __tablename__ = "navigation_items"

    id = Column(Integer, primary_key=True, index=True)
    label_en = Column(String(255), nullable=False)
    label_ar = Column(String(255))
    href = Column(String(255), nullable=False)
    icon = Column(String(100))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    parent_id = Column(Integer, ForeignKey("navigation_items.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
