"""
Collect every distinct asset URL from the database and verify the object
exists in S3 (via HEAD request). Reports any broken references.

Usage:
    python -m seeds.verify_s3_assets
"""
from __future__ import annotations

import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import SessionLocal

TARGETS = [
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
    ("product_images", "image_url"),
    ("product_categories", "image_url"),
    ("services", "image_url"),
    ("team_members", "image_url"),
    ("project_categories", "cover_image_url"),
    ("project_images", "image_url"),
    ("page_contents", "image_url"),
]


def head(url: str) -> int:
    # encode spaces etc. in the path
    parts = urllib.parse.urlsplit(url)
    safe_path = urllib.parse.quote(parts.path)
    encoded = urllib.parse.urlunsplit((parts.scheme, parts.netloc, safe_path, parts.query, parts.fragment))
    req = urllib.request.Request(encoded, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1


def main() -> int:
    db = SessionLocal()
    urls: dict[str, list[str]] = {}
    try:
        for table, column in TARGETS:
            try:
                rows = db.execute(text(
                    f"SELECT {column} FROM {table} WHERE {column} LIKE 'http%'"
                )).fetchall()
            except Exception:
                db.rollback()
                continue
            for (val,) in rows:
                if val:
                    urls.setdefault(val, []).append(f"{table}.{column}")
    finally:
        db.close()

    print(f"Distinct asset URLs referenced in DB: {len(urls)}")
    broken = []
    ok = 0
    for i, (url, sources) in enumerate(sorted(urls.items()), 1):
        status = head(url)
        if status == 200:
            ok += 1
        else:
            broken.append((url, status, sources))
        if i % 50 == 0:
            print(f"  ... checked {i}/{len(urls)}")

    print(f"\nOK: {ok}   BROKEN: {len(broken)}")
    for url, status, sources in broken:
        print(f"  [{status}] {url}   <- {', '.join(sorted(set(sources)))}")
    return 0 if not broken else 1


if __name__ == "__main__":
    sys.exit(main())
