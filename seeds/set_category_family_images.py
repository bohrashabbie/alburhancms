"""
Set product_categories.image_url to the S3 family plates (CMS-driven imagery).

Usage:
    python -m seeds.set_category_family_images            # dry run
    python -m seeds.set_category_family_images --apply
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.config import get_settings
from app.database import SessionLocal

settings = get_settings()
S3 = f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com"

# All 15 families -> public S3 URL served via CMS image_url
FAMILY_IMAGES = {
    "recessed-down-light": f"{S3}/site/renders/MS-240R.png",
    "surface-mounted-down-light": f"{S3}/site/renders/MS-252.png",
    "recessed-grille-spot-light": f"{S3}/site/renders/MS-220GR.png",
    "recessed-panel-light": f"{S3}/site/renders/MS-1140.png",
    "recessed-spot-light": f"{S3}/site/renders/MS-341AR.png",
    "track-spot-light": f"{S3}/site/families/track-spot-light.webp",
    "magnet-light": f"{S3}/site/families/magnet-light.webp",
    "linear-light": f"{S3}/site/families/linear-light.webp",
    "ceiling-light": f"{S3}/site/families/ceiling-light.webp",
    "high-bay": f"{S3}/site/families/high-bay.webp",
    "module-series": f"{S3}/site/families/module-series.webp",
    "wall-light": f"{S3}/site/families/wall-light.webp",
    "lawn-light": f"{S3}/site/families/lawn-light.webp",
    "street-light": f"{S3}/site/families/street-light.webp",
    "flood-light": f"{S3}/site/families/flood-light.webp",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    db = SessionLocal()
    updated = skipped = 0
    try:
        rows = db.execute(text("SELECT id, slug, image_url FROM product_categories")).fetchall()
        by_slug = {r[1]: (r[0], r[2]) for r in rows}
        print(f"[set_category_family_images] mode={'APPLY' if args.apply else 'DRY RUN'}\n")

        for slug, url in FAMILY_IMAGES.items():
            if slug not in by_slug:
                print(f"  SKIP missing category slug={slug}")
                skipped += 1
                continue
            pk, old = by_slug[slug]
            print(f"  {slug} id={pk}")
            print(f"    - {old}")
            print(f"    + {url}")
            if args.apply:
                db.execute(
                    text("UPDATE product_categories SET image_url = :u WHERE id = :id"),
                    {"u": url, "id": pk},
                )
            updated += 1

        if args.apply:
            db.commit()
            # bust public cache if API is up (best-effort)
            print(f"\ncommitted {updated} update(s), skipped {skipped}")
        else:
            print(f"\nwould update {updated}, skip {skipped}")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
