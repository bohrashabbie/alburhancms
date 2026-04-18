"""
Rewrite every "/uploads/..." path in the database to a full S3 URL.

Run after you've uploaded the files into the bucket (see
    seeds/upload_local_uploads_to_s3.py
). The S3 key layout must mirror the local uploads folder, e.g.:

    /uploads/Brands/brand1.png   ->   <S3_BASE>/Brands/brand1.png

Usage:
    python -m seeds.migrate_uploads_to_s3            # dry run, shows the diff
    python -m seeds.migrate_uploads_to_s3 --apply    # actually writes

Config comes from .env (STORAGE_BACKEND=s3, S3_BUCKET, AWS_REGION,
S3_PUBLIC_BASE_URL, S3_KEY_PREFIX).
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.config import get_settings
from app.database import SessionLocal
from app.models import *  # noqa: F401, F403  - ensures all models are registered

settings = get_settings()


def build_s3_base() -> str:
    if settings.S3_PUBLIC_BASE_URL:
        return settings.S3_PUBLIC_BASE_URL.rstrip("/")
    if not settings.S3_BUCKET:
        raise RuntimeError("S3_BUCKET is not configured in .env")
    return f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com"


# (table, column) pairs that store image-ish paths
TARGETS: list[Tuple[str, str]] = [
    ("media_files", "file_path"),
    ("site_settings", "value_en"),
    ("site_settings", "value_ar"),
    ("countries", "flag_url"),
    ("countries", "country_image_url"),
    ("countries", "logo_url"),
    ("carousel_slides", "image_url"),
    ("banners", "image_url"),
    ("brands", "logo_url"),
    ("products", "image_url"),
    ("services", "image_url"),
    ("team_members", "image_url"),
    ("project_categories", "cover_image_url"),
    ("project_images", "image_url"),
    ("page_contents", "image_url"),
]


def collect_rows(db) -> Iterable[Tuple[str, str, int, str]]:
    """Yield (table, column, id, current_value) for every row whose column
    starts with '/uploads/'."""
    for table, column in TARGETS:
        try:
            rows = db.execute(
                text(f"SELECT id, {column} FROM {table} WHERE {column} LIKE '/uploads/%'")
            ).fetchall()
        except Exception as e:
            print(f"  ! skipping {table}.{column}: {e}")
            continue
        for row in rows:
            yield table, column, row[0], row[1]


def rewrite_path(old: str, s3_base: str) -> str:
    # "/uploads/Brands/brand1.png" -> "<base>/Brands/brand1.png"
    tail = old[len("/uploads/"):] if old.startswith("/uploads/") else old.lstrip("/")
    prefix = settings.S3_KEY_PREFIX.strip("/")
    if prefix:
        return f"{s3_base}/{prefix}/{tail}"
    return f"{s3_base}/{tail}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually write changes (default: dry run)")
    args = parser.parse_args()

    s3_base = build_s3_base()
    print(f"[migrate_uploads_to_s3] S3 base: {s3_base}")
    print(f"[migrate_uploads_to_s3] mode   : {'APPLY' if args.apply else 'DRY RUN (pass --apply to commit)'}")
    print()

    db = SessionLocal()
    updated = 0
    try:
        for table, column, pk, old in collect_rows(db):
            new = rewrite_path(old, s3_base)
            print(f"  {table}.{column} id={pk}")
            print(f"    - {old}")
            print(f"    + {new}")
            if args.apply:
                db.execute(
                    text(f"UPDATE {table} SET {column} = :new WHERE id = :id"),
                    {"new": new, "id": pk},
                )
            updated += 1

        if args.apply:
            db.commit()
            print()
            print(f"[migrate_uploads_to_s3] committed {updated} row update(s)")
        else:
            print()
            print(f"[migrate_uploads_to_s3] would update {updated} row(s)  (dry run)")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
