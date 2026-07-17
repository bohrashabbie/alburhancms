"""
Scan every text/varchar column in the database for asset references that are
NOT S3 URLs: local "/uploads/..." paths, or absolute URLs pointing at the
server IP / any host serving "/uploads/".

Usage:
    python -m seeds.audit_asset_urls
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.database import SessionLocal


PATTERNS = [
    ("local_path", "%/uploads/%"),
    ("server_ip", "%13.60.4.75%"),
]


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
            for label, pattern in PATTERNS:
                try:
                    rows = db.execute(text(
                        f'SELECT id, "{column}" FROM "{table}" WHERE "{column}" LIKE :p LIMIT 200'
                    ), {"p": pattern}).fetchall()
                except Exception:
                    db.rollback()
                    continue
                for row in rows:
                    val = str(row[1])
                    # skip values already pointing at S3
                    if "amazonaws.com" in val and "/uploads/" not in val and "13.60.4.75" not in val:
                        continue
                    hits[(table, column, label)].append((row[0], val))

        if not hits:
            print("No non-S3 asset references found.")
            return 0

        total = 0
        for (table, column, label), rows in sorted(hits.items()):
            print(f"\n== {table}.{column}  [{label}]  ({len(rows)} rows)")
            for pk, val in rows[:10]:
                shown = val if len(val) < 160 else val[:157] + "..."
                print(f"   id={pk}: {shown}")
            if len(rows) > 10:
                print(f"   ... and {len(rows) - 10} more")
            total += len(rows)
        print(f"\nTOTAL: {total} row/column hits")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
