"""
Upload every file under ./uploads/ to the configured S3 bucket, preserving
folder structure and filenames. After this runs, a file at

    uploads/Brands/brand1.png

will be available at

    https://<bucket>.s3.<region>.amazonaws.com/Brands/brand1.png

(or the equivalent under S3_PUBLIC_BASE_URL / S3_KEY_PREFIX).

Usage:
    pip install boto3
    # fill AWS_* + S3_BUCKET in .env first
    python -m seeds.upload_local_uploads_to_s3
    python -m seeds.upload_local_uploads_to_s3 --dry-run
"""
from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings

settings = get_settings()

EXTS_AS_ATTACH = set()  # none for now; everything is served inline


def iter_files(root: Path):
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.startswith("."):
                continue
            yield Path(dirpath) / fn


def key_for(root: Path, path: Path) -> str:
    rel = path.relative_to(root).as_posix()
    prefix = settings.S3_KEY_PREFIX.strip("/")
    return f"{prefix}/{rel}" if prefix else rel


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="uploads", help="Local folder to upload (default: ./uploads)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                        help="Skip objects that already exist in the bucket (default on)")
    parser.add_argument("--overwrite", dest="skip_existing", action="store_false",
                        help="Re-upload even if the object already exists")
    args = parser.parse_args()

    if not settings.S3_BUCKET:
        print("ERROR: S3_BUCKET is not set in .env", file=sys.stderr)
        return 2

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 2

    print(f"[s3-upload] source bucket : {settings.S3_BUCKET} ({settings.AWS_REGION})")
    print(f"[s3-upload] key prefix    : '{settings.S3_KEY_PREFIX}'")
    print(f"[s3-upload] local root    : {root}")
    print(f"[s3-upload] mode          : {'DRY RUN' if args.dry_run else 'UPLOAD'}")
    print()

    import boto3  # type: ignore
    from botocore.exceptions import ClientError  # type: ignore

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    def object_exists(key: str) -> bool:
        try:
            s3.head_object(Bucket=settings.S3_BUCKET, Key=key)
            return True
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise

    uploaded = 0
    skipped = 0
    failed = 0

    for path in iter_files(root):
        key = key_for(root, path)
        if args.skip_existing and not args.dry_run and object_exists(key):
            skipped += 1
            continue

        ctype, _ = mimetypes.guess_type(str(path))
        ctype = ctype or "application/octet-stream"

        if args.dry_run:
            print(f"  DRY  {path}  ->  s3://{settings.S3_BUCKET}/{key}  ({ctype})")
            uploaded += 1
            continue

        try:
            with open(path, "rb") as f:
                s3.put_object(
                    Bucket=settings.S3_BUCKET,
                    Key=key,
                    Body=f.read(),
                    ContentType=ctype,
                )
            print(f"  OK   {key}")
            uploaded += 1
        except Exception as e:
            failed += 1
            print(f"  FAIL {key}  ({e})")

    print()
    print(f"[s3-upload] uploaded={uploaded}  skipped={skipped}  failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
