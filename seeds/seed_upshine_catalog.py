"""
Import products from UPSHINE Product Collection 2025-Ⅰ into the MS Lighting CMS.

Wisely:
  * Parse the catalogue TOC (pages 7–16) for MODEL / Pxxx entries
  * Map UPSHINE families onto the existing 15 MS Lighting categories
  * Skip drivers, strip lights, junction boxes, and other non-fixture accessories
  * Prefer NEW-marked models first; then fill each category up to --per-category
  * Render the catalogue product page as the hero image → upload to S3
  * Upsert products + product_images + search_aliases (idempotent by slug)

Usage:
    python -m seeds.seed_upshine_catalog --dry-run
    python -m seeds.seed_upshine_catalog --apply
    python -m seeds.seed_upshine_catalog --apply --per-category 6
"""
from __future__ import annotations

import argparse
import io
import mimetypes
import os
import re
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz
from PIL import Image
from sqlalchemy import text

from app.config import get_settings
from app.database import SessionLocal, engine, Base
from app.models import Product, ProductCategory, ProductImage, SearchAlias

settings = get_settings()

PDF = Path(r"c:\dumbstack\ab1\UPSHINE Product Collection 2025-Ⅰ (2).pdf")
# Printed page P002 appears on PDF page 19 → offset 17
PRINT_TO_PDF_OFFSET = 17
S3_FOLDER = "ms-lighting/products/upshine"
TOC_PAGES = range(6, 16)  # 0-based: PDF pages 7–16

# Section headers in TOC → MS category slug
SECTION_MAP = [
    (re.compile(r"recessed\s+downlight", re.I), "recessed-down-light"),
    (re.compile(r"fire-?rated\s+downlight", re.I), "recessed-down-light"),
    (re.compile(r"mini\s+downlight", re.I), "recessed-down-light"),
    (re.compile(r"surface\s+mounted\s+downlight", re.I), "surface-mounted-down-light"),
    (re.compile(r"48v\s+track\s+light", re.I), "magnet-light"),
    (re.compile(r"led\s+track\s+light", re.I), "track-spot-light"),
    (re.compile(r"^track\s+light", re.I), "track-spot-light"),
    (re.compile(r"led\s+ceiling\s+light", re.I), "ceiling-light"),
    (re.compile(r"led\s+bulkhead", re.I), "ceiling-light"),
    (re.compile(r"led\s+panel\s+light", re.I), "recessed-panel-light"),
    (re.compile(r"office\s+lighting", re.I), "linear-light"),
    (re.compile(r"led\s+linear", re.I), "linear-light"),
    (re.compile(r"led\s+tube", re.I), "linear-light"),
    (re.compile(r"^pendant", re.I), "ceiling-light"),
    (re.compile(r"^wall\s+light", re.I), "wall-light"),
    (re.compile(r"solar\s+wall", re.I), "wall-light"),
    (re.compile(r"spike\s+light", re.I), "lawn-light"),
    (re.compile(r"^bollard", re.I), "lawn-light"),
    (re.compile(r"bed\s+light", re.I), "wall-light"),
    (re.compile(r"mirror\s+light", re.I), "wall-light"),
    (re.compile(r"vandal\s+resistant", re.I), "wall-light"),
]

SKIP_SECTION = re.compile(
    r"led\s+strip|led\s+driver|constant\s+current|constant\s+voltage|"
    r"junction\s+box|connection\s+wire|emergency\s+led\s+driver|"
    r"driver\s+solution|smart\s+wireless",
    re.I,
)

# MODEL / Pxxx  (also MODEL/Pxxx and multi-code MODEL&MODEL)
ENTRY_RE = re.compile(
    r"(?P<code>[A-Z]{1,6}(?:-?[A-Z0-9]+)+(?:/[A-Z0-9]+)*)\s*/\s*P(?P<page>\d{2,4})",
    re.I,
)
# Mark NEW blocks — we tag the following few entries
NEW_RE = re.compile(r"^\s*NEW\s*$", re.I)

CATEGORY_NAMES = {
    "recessed-down-light": "Recessed Down Light",
    "surface-mounted-down-light": "Surface Mounted Down Light",
    "recessed-grille-spot-light": "Recessed Grille Spot Light",
    "recessed-panel-light": "Recessed Panel Light",
    "recessed-spot-light": "Recessed Spot Light",
    "track-spot-light": "Track Spot Light",
    "magnet-light": "Magnet Light",
    "linear-light": "Linear Light",
    "ceiling-light": "Ceiling Light",
    "high-bay": "High Bay",
    "module-series": "Module Series",
    "wall-light": "Wall Light",
    "lawn-light": "Lawn Light",
    "street-light": "Street Light",
    "flood-light": "Flood Light",
}


def category_from_code(code: str, toc_hint: str | None) -> str | None:
    """Prefer model-code prefix (TOC columns are jumbled in text extraction)."""
    c = code.upper()
    if c.startswith(("DC-TL", "DC-PD", "ART-DC-TL", "ART-DC-PD", "ART-TL", "ART-PD")):
        return "magnet-light"
    if c.startswith(("TL",)):
        return "track-spot-light"
    if c.startswith(("PL-", "PL0", "PL1", "PL2", "PL3", "PL4", "PL5", "PL6", "PL7", "PL8", "PL9", "PLAK")):
        return "recessed-panel-light"
    if c.startswith(("DB", "T5", "T8", "OL", "TRP")):
        return "linear-light"
    if c.startswith(("WL", "ML")):
        return "wall-light"
    if c.startswith(("KL",)):
        return "recessed-down-light"  # mini / cabinet
    if c.startswith(("NL", "SOL")):
        return "lawn-light"
    if c.startswith(("FL", "HB")):
        return "flood-light" if c.startswith("FL") else "high-bay"
    if c.startswith(("AL", "PD")):
        return "ceiling-light"
    if c.startswith(("RD", "CK", "GL", "DR")):
        return "module-series"
    if c.startswith(("CL",)):
        # UPSHINE CL* is often surface/ceiling; residential CL near surface pages stay surface
        if toc_hint == "surface-mounted-down-light":
            return "surface-mounted-down-light"
        return "ceiling-light"
    if c.startswith(("DL",)):
        if toc_hint == "surface-mounted-down-light":
            return "surface-mounted-down-light"
        return "recessed-down-light"
    if c.startswith(("TH",)):
        return "recessed-spot-light"
    return toc_hint if toc_hint in CATEGORY_NAMES else None


@dataclass
class TocEntry:
    model_code: str
    print_page: int
    category_slug: str
    is_new: bool = False


def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:120]


def parse_toc(doc: fitz.Document) -> list[TocEntry]:
    current_cat: str | None = None
    skip = False
    pending_new = 0
    entries: list[TocEntry] = []
    seen: set[str] = set()

    for pi in TOC_PAGES:
        text = doc[pi].get_text("text")
        # Join hyphenated line-breaks only: "DC-TL142-\n3710-18W / P542"
        text = re.sub(r"-\s*\n\s*", "-", text)
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            if NEW_RE.match(line):
                pending_new = 8
                continue
            if SKIP_SECTION.search(line):
                skip = True
                current_cat = None
                continue
            # Section header (with or without page range), not a product entry
            if not ENTRY_RE.search(line):
                for rx, slug in SECTION_MAP:
                    if rx.search(line):
                        current_cat = slug
                        skip = False
                        break

            if skip or not current_cat:
                continue

            for m in ENTRY_RE.finditer(line):
                code = m.group("code").upper().replace(" ", "")
                # Expand A&B / A/B variants into primary code only
                primary = re.split(r"[&/]", code)[0]
                primary = primary.strip("-")
                if len(primary) < 3:
                    continue
                if primary in seen:
                    continue
                # Filter voltage / finish junk that slipped through
                if re.match(r"^(AC|DC|RAL|CRI|IK|IP|TH)\d", primary):
                    continue
                if primary.startswith("ST") and "COB" in code:
                    continue
                page = int(m.group("page"))
                is_new = pending_new > 0
                if pending_new > 0:
                    pending_new -= 1
                cat = category_from_code(primary, current_cat)
                if not cat:
                    continue
                seen.add(primary)
                entries.append(
                    TocEntry(
                        model_code=primary,
                        print_page=page,
                        category_slug=cat,
                        is_new=is_new,
                    )
                )
    return entries


def select_wisely(entries: list[TocEntry], per_category: int) -> list[TocEntry]:
    """NEW first, then fill each category up to per_category."""
    by_cat: dict[str, list[TocEntry]] = defaultdict(list)
    for e in entries:
        by_cat[e.category_slug].append(e)

    chosen: list[TocEntry] = []
    for slug, items in sorted(by_cat.items()):
        news = [x for x in items if x.is_new]
        rest = [x for x in items if not x.is_new]
        # stable order: NEW first, then TOC order
        ordered = news + rest
        take = ordered[:per_category]
        chosen.extend(take)
        print(f"  [{slug}] toc={len(items)} new={len(news)} selected={len(take)}")
    return chosen


def print_to_pdf_index(print_page: int) -> int:
    return print_page + PRINT_TO_PDF_OFFSET - 1  # 0-based


def render_hero(doc: fitz.Document, print_page: int) -> bytes:
    idx = print_to_pdf_index(print_page)
    idx = max(0, min(idx, doc.page_count - 1))
    page = doc[idx]
    pix = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    # Soft crop: drop heavy margins, keep product frame
    w, h = img.size
    img = img.crop((int(w * 0.04), int(h * 0.06), int(w * 0.96), int(h * 0.94)))
    img.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=82, method=4)
    return buf.getvalue()


def s3_upload_bytes(data: bytes, ext: str = ".webp") -> str:
    import boto3

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    key = f"{S3_FOLDER}/{uuid.uuid4().hex}{ext}"
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=data,
        ContentType="image/webp",
        CacheControl="public, max-age=31536000, immutable",
    )
    if settings.S3_PUBLIC_BASE_URL:
        return f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{key}"
    return f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"


def ensure_schema():
    Base.metadata.create_all(bind=engine)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--per-category", type=int, default=8, help="max products per MS category")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    apply = args.apply and not args.dry_run

    if not PDF.exists():
        print(f"ERROR: PDF not found: {PDF}", file=sys.stderr)
        return 2

    print("[upshine] opening catalogue PDF ...")
    doc = fitz.open(PDF)
    entries = parse_toc(doc)
    print(f"[upshine] TOC entries parsed: {len(entries)}")
    selected = select_wisely(entries, args.per_category)
    print(f"[upshine] selected: {len(selected)}  mode={'APPLY' if apply else 'DRY RUN'}")

    if not apply:
        for e in selected[:40]:
            print(f"  DRY  {e.model_code:<16} [{e.category_slug}]  P{e.print_page:03d}{'  NEW' if e.is_new else ''}")
        if len(selected) > 40:
            print(f"  … +{len(selected) - 40} more")
        return 0

    if not settings.S3_BUCKET:
        print("ERROR: S3_BUCKET not set", file=sys.stderr)
        return 2

    ensure_schema()
    db = SessionLocal()
    created = updated = skipped = 0
    cat_cache: dict[str, ProductCategory] = {}

    try:
        for i, e in enumerate(selected, 1):
            cat_slug = e.category_slug
            cat_name = CATEGORY_NAMES.get(cat_slug, cat_slug)
            slug = slugify(e.model_code)

            cat = cat_cache.get(cat_slug)
            if not cat:
                cat = db.query(ProductCategory).filter(ProductCategory.slug == cat_slug).first()
                if not cat:
                    cat = ProductCategory(
                        slug=cat_slug,
                        name_en=cat_name,
                        seo_title=f"{cat_name} | MS Lighting",
                        seo_description=f"Browse {cat_name} LED fixtures from MS Lighting.",
                        seo_keywords=f"{cat_name}, {cat_slug}, led, lighting, ms lighting",
                        sort_order=100 + i,
                    )
                    db.add(cat)
                    db.flush()
                cat_cache[cat_slug] = cat

            try:
                hero_bytes = render_hero(doc, e.print_page)
                hero_url = s3_upload_bytes(hero_bytes)
            except Exception as ex:
                print(f"  FAIL image {e.model_code}: {ex}")
                skipped += 1
                continue

            name_en = e.model_code
            prod = db.query(Product).filter(Product.slug == slug).first()
            is_new = prod is None
            if is_new:
                prod = Product(slug=slug)
                db.add(prod)
            prod.model_code = e.model_code
            prod.category_id = cat.id
            prod.name_en = name_en
            prod.description_en = (
                f"{e.model_code} — {cat_name}. Sourced from UPSHINE Product Collection 2025-Ⅰ "
                f"(catalogue page {e.print_page:03d}). Professional LED fixture for commercial "
                f"and residential projects."
            )
            prod.image_url = hero_url
            prod.spec_image_url = hero_url  # same plate; catalogue page holds specs too
            prod.seo_title = f"{e.model_code} {cat_name} | MS Lighting"
            prod.seo_description = (
                f"{e.model_code} {cat_name} LED fixture — specifications and product data from MS Lighting."
            )
            prod.seo_keywords = ", ".join(
                [e.model_code, cat_name, cat_slug, "led", "upshine", "ms lighting"]
            )
            prod.sort_order = 200 + i
            prod.is_active = True
            db.flush()

            db.query(ProductImage).filter(ProductImage.product_id == prod.id).delete()
            db.add(
                ProductImage(
                    product_id=prod.id, image_url=hero_url, image_type="hero", sort_order=0
                )
            )

            target_url = f"/products/{cat_slug}/{slug}"
            db.query(SearchAlias).filter(
                SearchAlias.target_slug == slug, SearchAlias.target_type == "product"
            ).delete()
            for kw in {e.model_code.lower(), e.model_code.replace("-", " ").lower()}:
                db.add(
                    SearchAlias(
                        keyword=kw,
                        target_type="product",
                        target_slug=slug,
                        target_url=target_url,
                        is_redirect=True,
                        weight=10,
                    )
                )

            if is_new:
                created += 1
                print(f"  + {e.model_code} → {cat_slug}")
            else:
                updated += 1
                print(f"  ~ {e.model_code} → {cat_slug}")

            if i % 10 == 0:
                db.commit()

        db.commit()
        print(f"\n[upshine] created={created} updated={updated} skipped={skipped}")
        print("[upshine] invalidate public cache: POST /api/public/cache/invalidate")
    finally:
        db.close()
        doc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
