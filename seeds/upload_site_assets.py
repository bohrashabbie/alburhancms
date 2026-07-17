"""
Upload the MS-Lighting web/public media (banners, markets, renders, scenes,
video) to S3 under the "site/" prefix, preserving folder structure.

logo.png / favicons stay in /public (small chrome cached by Next).

Usage:
    python -m seeds.upload_site_assets --root "c:/dumbstack/ab1/web/public"
"""
from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
from app.config import get_settings

settings = get_settings()

FOLDERS = ["banners", "markets", "renders", "scenes", "video"]
PREFIX = "site"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    uploaded = failed = 0
    for folder in FOLDERS:
        d = root / folder
        if not d.is_dir():
            print(f"  ! missing folder: {d}")
            continue
        for path in sorted(d.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            key = f"{PREFIX}/{rel}"
            ctype, _ = mimetypes.guess_type(str(path))
            ctype = ctype or "application/octet-stream"
            if args.dry_run:
                print(f"  DRY  {rel} -> s3://{settings.S3_BUCKET}/{key} ({ctype})")
                uploaded += 1
                continue
            try:
                with open(path, "rb") as f:
                    s3.put_object(
                        Bucket=settings.S3_BUCKET,
                        Key=key,
                        Body=f.read(),
                        ContentType=ctype,
                        CacheControl="public, max-age=31536000, immutable",
                    )
                print(f"  OK   {key}")
                uploaded += 1
            except Exception as e:
                failed += 1
                print(f"  FAIL {key} ({e})")

    print(f"\nuploaded={uploaded} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
