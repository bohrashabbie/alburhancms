"""
Rewrite root-relative asset paths (e.g. "/OurProject/.../img.jpg") to full
S3 URLs. Only rewrites when the matching object exists in the bucket.

Usage:
    python -m seeds.rewrite_relative_to_s3            # dry run
    python -m seeds.rewrite_relative_to_s3 --apply    # commit changes
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

import boto3
from app.config import get_settings
from app.database import SessionLocal

settings = get_settings()

TARGETS = [
    ("project_categories", "cover_image_url"),
    ("project_images", "image_url"),
]

EXT_RE = re.compile(r"\.(png|jpe?g|webp|gif|svg|ico|pdf|mp4|avif)$", re.IGNORECASE)


def s3_base() -> str:
    if settings.S3_PUBLIC_BASE_URL:
        return settings.S3_PUBLIC_BASE_URL.rstrip("/")
    return f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    base = s3_base()
    print(f"[rewrite] S3 base: {base}")
    print(f"[rewrite] mode   : {'APPLY' if args.apply else 'DRY RUN'}\n")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    def in_s3(key: str) -> bool:
        try:
            s3.head_object(Bucket=settings.S3_BUCKET, Key=key)
            return True
        except Exception:
            return False

    db = SessionLocal()
    updated = skipped = 0
    try:
        for table, column in TARGETS:
            rows = db.execute(text(
                f"SELECT id, {column} FROM {table} "
                f"WHERE {column} LIKE '/%' AND {column} NOT LIKE 'http%'"
            )).fetchall()
            for pk, val in rows:
                if not EXT_RE.search(val or ""):
                    continue
                key = val.lstrip("/")
                if not in_s3(key):
                    print(f"  SKIP (missing in S3) {table}.{column} id={pk}: {val}")
                    skipped += 1
                    continue
                # URL-encode the path (spaces, parentheses, etc.)
                new = f"{base}/{quote(key)}"
                print(f"  {table}.{column} id={pk}")
                print(f"    - {val}")
                print(f"    + {new}")
                if args.apply:
                    db.execute(
                        text(f"UPDATE {table} SET {column} = :new WHERE id = :id"),
                        {"new": new, "id": pk},
                    )
                updated += 1
        if args.apply:
            db.commit()
            print(f"\n[rewrite] committed {updated} update(s), skipped {skipped}")
        else:
            print(f"\n[rewrite] would update {updated} row(s), skip {skipped}  (dry run)")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
