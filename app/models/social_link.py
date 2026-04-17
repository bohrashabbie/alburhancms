from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SocialLink(Base):
    __tablename__ = "social_links"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    icon = Column(String(100))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
