from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    image_url = Column(String(500), nullable=False)
    # "hero"  -> catalog page 1 (product photo)
    # "spec"  -> catalog page 2 (specifications / technical data)
    # "gallery" -> any extra image
    image_type = Column(String(30), nullable=False, default="gallery")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
