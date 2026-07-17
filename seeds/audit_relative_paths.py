"""
Find every DB value that looks like a root-relative asset path (starts with
"/" and has an image/file extension) — these are NOT served from S3.
Also checks whether a matching object exists in the S3 bucket.

Usage:
    python -m seeds.audit_relative_paths
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

import boto3
from app.config import get_settings
from app.database import SessionLocal

settings = get_settings()

EXT_RE = re.compile(r"\.(png|jpe?g|webp|gif|svg|ico|pdf|mp4|avif)$", re.IGNORECASE)


def main() -> int:
    db = SessionLocal()
    hits = defaultdict(list)
    try:
        cols = db.execute(text(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND data_type IN ('text', 'character varying')
            ORDER BY table_name, column_name
            """
        )).fetchall()

        for table, column in cols:
            try:
                rows = db.execute(text(
                    f'SELECT id, "{column}" FROM "{table}" WHERE "{column}" LIKE \'/%\''
                )).fetchall()
            except Exception:
                db.rollback()
                continue
            for pk, val in rows:
                v = str(val)
                if v.startswith("//") or v.startswith("/api/"):
                    continue
                if EXT_RE.search(v):
                    hits[(table, column)].append((pk, v))
    finally:
        db.close()

    if not hits:
        print("No root-relative asset paths found.")
        return 0

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

    total = 0
    missing = 0
    for (table, column), rows in sorted(hits.items()):
        print(f"\n== {table}.{column}  ({len(rows)} rows)")
        for pk, v in rows:
            key = v.lstrip("/")
            exists = in_s3(key)
            mark = "S3-OK " if exists else "S3-MISSING"
            if not exists:
                missing += 1
            print(f"   [{mark}] id={pk}: {v}")
            total += 1
    print(f"\nTOTAL: {total} relative paths, {missing} missing from S3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
