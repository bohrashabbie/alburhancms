"""Upload isolated (transparent) product cut-outs to S3 and point products at them.

Reads extract/cut/<slug>.png, uploads to S3 (ms-lighting/products/cut), and sets
product.image_url (+ the 'hero' ProductImage) to the cut-out URL so cards/detail
show the fixture on a dark background. Spec images are left untouched.
"""
import os, sys, uuid, mimetypes
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import get_settings
from app.database import SessionLocal
from app.models import Product, ProductImage

s = get_settings()
CUT = Path(__file__).resolve().parent.parent.parent / "MS-Lighting" / "extract" / "cut"
import boto3
s3 = boto3.client("s3", aws_access_key_id=s.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=s.AWS_SECRET_ACCESS_KEY, region_name=s.AWS_REGION)

def upload(path: Path) -> str:
    key = f"ms-lighting/products/cut/{uuid.uuid4().hex}.png"
    s3.put_object(Bucket=s.S3_BUCKET, Key=key, Body=path.read_bytes(), ContentType="image/png")
    return f"https://{s.S3_BUCKET}.s3.{s.AWS_REGION}.amazonaws.com/{key}"

db = SessionLocal()
n = 0
for png in sorted(CUT.glob("*.png")):
    slug = png.stem
    prod = db.query(Product).filter(Product.slug == slug).first()
    if not prod:
        print("  ? no product for", slug); continue
    url = upload(png)
    prod.image_url = url
    hero = db.query(ProductImage).filter(ProductImage.product_id == prod.id,
                                         ProductImage.image_type == "hero").first()
    if hero:
        hero.image_url = url
    else:
        db.add(ProductImage(product_id=prod.id, image_url=url, image_type="hero", sort_order=0))
    n += 1
    print("  ok", slug)
db.commit()
db.close()
print(f"[cut-upload] updated {n} products")
