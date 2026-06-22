"""
Seed MS-Lighting products from the catalog extraction manifest.

Reads a manifest.json produced by MS-Lighting/extract/build_pipeline.py, uploads
each product's hero + spec WebP image to S3 (same backend the CMS uses), and
upserts:

  * product_categories   (one row per distinct category)
  * products             (slug, model_code, category, hero + spec image URLs)
  * product_images       (hero + spec rows)
  * search_aliases       (model code + name variants -> product page)

Idempotent: re-running updates existing rows (matched by slug) and skips images
already uploaded (tracked in the manifest via *_url fields).

Usage:
    # 1. ensure AWS_* + S3_BUCKET are set in alburhancms/.env
    python -m seeds.seed_products_from_catalog \
        --manifest ../MS-Lighting/extract/manifest.json \
        --images   ../MS-Lighting/extract/web

    python -m seeds.seed_products_from_catalog ... --dry-run     # no S3, no DB writes
    python -m seeds.seed_products_from_catalog ... --no-upload   # DB only, reuse URLs in manifest
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import uuid
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.database import SessionLocal, engine, Base
from app.models import Product, ProductCategory, ProductImage, SearchAlias

settings = get_settings()

S3_FOLDER = "ms-lighting/products"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def ensure_schema():
    """Create new tables and add new product columns if missing (idempotent)."""
    Base.metadata.create_all(bind=engine)
    alters = [
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS slug VARCHAR(255)",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS model_code VARCHAR(120)",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS category_id INTEGER",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS spec_image_url VARCHAR(500)",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS seo_title VARCHAR(255)",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS seo_description TEXT",
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS seo_keywords TEXT",
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_products_slug ON products (slug)",
        "CREATE INDEX IF NOT EXISTS ix_products_model_code ON products (model_code)",
    ]
    from sqlalchemy import text
    with engine.begin() as conn:
        for stmt in alters:
            conn.execute(text(stmt))
    print("[schema] tables + product columns ensured")


def s3_upload(local: Path) -> str:
    import boto3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    ext = local.suffix
    key_parts = []
    if settings.S3_KEY_PREFIX:
        key_parts.append(settings.S3_KEY_PREFIX.strip("/"))
    key_parts.append(S3_FOLDER)
    key_parts.append(f"{uuid.uuid4().hex}{ext}")
    key = "/".join(key_parts)
    ctype = mimetypes.guess_type(str(local))[0] or "image/webp"
    with open(local, "rb") as f:
        s3.put_object(Bucket=settings.S3_BUCKET, Key=key, Body=f.read(), ContentType=ctype)
    if settings.S3_PUBLIC_BASE_URL:
        return f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{key}"
    return f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--images", required=True, help="folder with the webp images")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-upload", action="store_true", help="skip S3, reuse *_url already in manifest")
    args = ap.parse_args()

    manifest_path = Path(args.manifest).resolve()
    images_dir = Path(args.images).resolve()
    data = json.loads(manifest_path.read_text())
    products = data["products"]

    do_upload = not args.no_upload and not args.dry_run
    if do_upload and not settings.S3_BUCKET:
        print("ERROR: S3_BUCKET not set. Add AWS creds to .env or use --no-upload.", file=sys.stderr)
        return 2

    if not args.dry_run:
        ensure_schema()
        db = SessionLocal()
    else:
        db = None

    cat_cache: dict[str, ProductCategory] = {}
    created = updated = skipped = 0

    for p in products:
        if p.get("needs_review") and not p.get("model_code"):
            skipped += 1
            continue
        model_code = (p.get("model_code") or "").strip()
        category_name = (p.get("category") or "Uncategorized").strip()
        if not model_code:
            skipped += 1
            continue

        slug = slugify(model_code)
        cat_slug = slugify(category_name)
        name_en = p.get("name_en") or model_code

        # --- upload images ---
        hero_url = p.get("hero_url")
        spec_url = p.get("spec_url")
        if do_upload:
            if not hero_url and p.get("hero_file"):
                hf = images_dir / p["hero_file"]
                if hf.exists():
                    hero_url = s3_upload(hf); p["hero_url"] = hero_url
            if not spec_url and p.get("spec_file"):
                sf = images_dir / p["spec_file"]
                if sf.exists():
                    spec_url = s3_upload(sf); p["spec_url"] = spec_url

        if args.dry_run:
            print(f"  DRY  #{p['index']:>3}  {model_code:<14} [{category_name}]  hero={p.get('hero_file')} spec={p.get('spec_file')}")
            continue

        # --- category upsert ---
        cat = cat_cache.get(cat_slug)
        if not cat:
            cat = db.query(ProductCategory).filter(ProductCategory.slug == cat_slug).first()
            if not cat:
                cat = ProductCategory(
                    slug=cat_slug, name_en=category_name,
                    seo_title=f"{category_name} | MS Lighting",
                    seo_description=f"Browse {category_name} LED fixtures from MS Lighting.",
                    seo_keywords=f"{category_name}, {cat_slug}, led, lighting, ms lighting",
                    sort_order=p["index"],
                )
                db.add(cat); db.flush()
            cat_cache[cat_slug] = cat

        # --- product upsert ---
        prod = db.query(Product).filter(Product.slug == slug).first()
        is_new = prod is None
        if is_new:
            prod = Product(slug=slug)
            db.add(prod)
        prod.model_code = model_code
        prod.category_id = cat.id
        prod.name_en = name_en
        prod.image_url = hero_url
        prod.spec_image_url = spec_url
        prod.seo_title = f"{model_code} {category_name} | MS Lighting"
        prod.seo_description = f"{model_code} — {category_name}. Specifications, technical data and certifications from MS Lighting."
        prod.seo_keywords = ", ".join(filter(None, [model_code, model_code.replace("-", " "), category_name, cat_slug, "led", "ms lighting"]))
        prod.sort_order = p["index"]
        prod.is_active = True
        db.flush()

        # --- product images (replace) ---
        db.query(ProductImage).filter(ProductImage.product_id == prod.id).delete()
        if hero_url:
            db.add(ProductImage(product_id=prod.id, image_url=hero_url, image_type="hero", sort_order=0))
        if spec_url:
            db.add(ProductImage(product_id=prod.id, image_url=spec_url, image_type="spec", sort_order=1))

        # --- search aliases (replace for this product) ---
        target_url = f"/products/{cat_slug}/{slug}"
        db.query(SearchAlias).filter(SearchAlias.target_slug == slug, SearchAlias.target_type == "product").delete()
        keywords = {model_code.lower(), model_code.replace("-", " ").lower(), name_en.lower()}
        for kw in filter(None, keywords):
            db.add(SearchAlias(keyword=kw, target_type="product", target_slug=slug,
                               target_url=target_url, is_redirect=True, weight=10))

        if is_new:
            created += 1
        else:
            updated += 1

    if not args.dry_run:
        # one alias per category -> category page
        for cat in cat_cache.values():
            db.query(SearchAlias).filter(SearchAlias.target_slug == cat.slug, SearchAlias.target_type == "category").delete()
            db.add(SearchAlias(keyword=cat.name_en.lower(), target_type="category",
                               target_slug=cat.slug, target_url=f"/products/{cat.slug}",
                               is_redirect=True, weight=5))
        db.commit()
        db.close()
        # persist any newly uploaded URLs back to the manifest
        manifest_path.write_text(json.dumps(data, indent=2))

    print(f"\n[seed] created={created} updated={updated} skipped={skipped} categories={len(cat_cache)}")
    if not args.dry_run:
        print("[seed] remember to POST /api/public/cache/invalidate (or restart) to clear the public cache")
    return 0


if __name__ == "__main__":
    sys.exit(main())
