from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ProjectCategory(Base):
    __tablename__ = "project_categories"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    cover_image_url = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    projects = relationship("Project", back_populates="category")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("project_categories.id", ondelete="SET NULL"))
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"))
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    description_en = Column(Text)
    description_ar = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("ProjectCategory", back_populates="projects")
    country = relationship("Country", back_populates="projects")
    images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")


class ProjectImage(Base):
    __tablename__ = "project_images"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="images")
