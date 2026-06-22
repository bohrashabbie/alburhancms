"""Give each product category a thumbnail = its first product's hero image."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from app.models import ProductCategory, Product

db = SessionLocal()
n = 0
for cat in db.query(ProductCategory).all():
    first = (
        db.query(Product)
        .filter(Product.category_id == cat.id, Product.is_active == True, Product.image_url.isnot(None))
        .order_by(Product.sort_order)
        .first()
    )
    if first and first.image_url:
        cat.image_url = first.image_url
        n += 1
        print(f"  {cat.slug:<28} -> {first.model_code} (isolated)")
db.commit()
db.close()
print(f"[category-images] set {n} category thumbnails")
