from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SearchAlias(Base):
    """Admin-managed mapping from a search keyword to a target page.

    When a visitor searches the site, the query is matched (case/space/dash
    insensitive) against these aliases as well as product model codes and
    names. An alias with is_redirect=True sends the visitor straight to
    target_url instead of a results list.
    """
    __tablename__ = "search_aliases"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), index=True, nullable=False)
    # "product" | "category"
    target_type = Column(String(30), nullable=False, default="product")
    # slug of the product or category this keyword resolves to
    target_slug = Column(String(255), nullable=False)
    # pre-built front-end path, e.g. /products/recessed-down-light/ms-240r
    target_url = Column(String(500))
    is_redirect = Column(Boolean, nullable=False, default=True)
    weight = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
