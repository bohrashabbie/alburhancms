from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, index=True)
    model_code = Column(String(120), index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="SET NULL"), index=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    description_en = Column(Text)
    description_ar = Column(Text)
    image_url = Column(String(500))            # hero image (catalog page 1)
    spec_image_url = Column(String(500))       # specifications image (catalog page 2)
    # SEO
    seo_title = Column(String(255))
    seo_description = Column(Text)
    seo_keywords = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("ProductCategory", backref="products", lazy="joined")
    images = relationship(
        "ProductImage",
        primaryjoin="Product.id==ProductImage.product_id",
        order_by="ProductImage.sort_order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
