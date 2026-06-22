"""Public API endpoints for the Next.js frontend - no auth required.

All GET endpoints use an in-memory TTL cache (see app.utils.cache) so
repeated requests within the TTL window bypass the database entirely.
Any CMS write operation automatically invalidates the cache.

Responses also carry a Cache-Control header so CDNs / browsers can
serve stale content while revalidating in the background.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import get_settings
from app.utils.mailer import send_email
from app.models import (
    SiteSetting, NavigationItem, CarouselSlide, PageContent,
    Service, Sector, TeamMember, Country, ContactInfo,
    SocialLink, Brand, Product, Banner, ProjectCategory,
    FooterLink, StaticPage, ContactSubmission,
    ProductCategory, ProductImage, SearchAlias,
)
from app.schemas.schemas import (
    FullSiteContentOut, ContactSubmissionCreate, ContactSubmissionOut,
    SiteSettingOut, NavigationItemOut, CarouselSlideOut, PageContentOut,
    ServiceOut, SectorOut, TeamMemberOut, CountryOut, ContactInfoOut,
    SocialLinkOut, BrandOut, ProductOut, BannerOut, ProjectCategoryOut,
    FooterLinkOut, StaticPageOut, ProductCategoryOut,
)
from app.utils import cache as app_cache

router = APIRouter(prefix="/api/public", tags=["Public API"])

# ---------------------------------------------------------------------------
# Cache-Control header value for all public GET responses
# max-age=30  : browsers / Next.js may reuse for 30 s without re-fetching
# s-maxage=60 : shared caches (CDN) may keep for 60 s
# stale-while-revalidate=120 : serve stale for up to 120 s while refreshing
# ---------------------------------------------------------------------------
CACHE_CONTROL = "public, max-age=30, s-maxage=60, stale-while-revalidate=120"


def _cached_json(cache_key: str, builder, status_code: int = 200):
    """Return cached JSON response or build, cache, and return it."""
    cached = app_cache.get(cache_key)
    if cached is not None:
        return JSONResponse(content=cached, headers={"Cache-Control": CACHE_CONTROL, "X-Cache": "HIT"})
    result = builder()
    # Pydantic model → dict for JSON serialisation
    if hasattr(result, "model_dump"):
        data = result.model_dump(mode="json")
    elif isinstance(result, list):
        data = [r.model_dump(mode="json") if hasattr(r, "model_dump") else r for r in result]
    else:
        data = result
    app_cache.put(cache_key, data)
    return JSONResponse(content=data, headers={"Cache-Control": CACHE_CONTROL, "X-Cache": "MISS"})


# ---------------------------------------------------------------------------
# Cache invalidation endpoint (called by admin or CRUD hooks)
# ---------------------------------------------------------------------------

@router.post("/cache/invalidate")
def invalidate_cache():
    """Clear all cached public data. Call after any CMS write."""
    app_cache.invalidate_all()
    return {"ok": True, "message": "Cache cleared"}


# ---------------------------------------------------------------------------
# Public GET endpoints — all cached
# ---------------------------------------------------------------------------

@router.get("/site-content")
def get_full_site_content(db: Session = Depends(get_db)):
    """Single endpoint to fetch ALL site content for the frontend."""
    def _build():
        return FullSiteContentOut(
            settings=db.query(SiteSetting).all(),
            navigation=db.query(NavigationItem).filter(NavigationItem.is_active == True).order_by(NavigationItem.sort_order).all(),
            carousel_slides=db.query(CarouselSlide).filter(CarouselSlide.is_active == True).order_by(CarouselSlide.sort_order).all(),
            page_contents=db.query(PageContent).filter(PageContent.is_active == True).order_by(PageContent.sort_order).all(),
            services=db.query(Service).filter(Service.is_active == True).order_by(Service.sort_order).all(),
            sectors=db.query(Sector).filter(Sector.is_active == True).order_by(Sector.sort_order).all(),
            team_members=db.query(TeamMember).filter(TeamMember.is_active == True).order_by(TeamMember.sort_order).all(),
            countries=db.query(Country).filter(Country.is_active == True).order_by(Country.sort_order).all(),
            contact_info=db.query(ContactInfo).filter(ContactInfo.is_active == True).all(),
            social_links=db.query(SocialLink).filter(SocialLink.is_active == True).order_by(SocialLink.sort_order).all(),
            brands=db.query(Brand).filter(Brand.is_active == True).order_by(Brand.sort_order).all(),
            products=db.query(Product).filter(Product.is_active == True).order_by(Product.sort_order).all(),
            banners=db.query(Banner).filter(Banner.is_active == True).order_by(Banner.sort_order).all(),
            project_categories=db.query(ProjectCategory).filter(ProjectCategory.is_active == True).order_by(ProjectCategory.sort_order).all(),
            footer_links=db.query(FooterLink).filter(FooterLink.is_active == True).order_by(FooterLink.sort_order).all(),
            static_pages=db.query(StaticPage).filter(StaticPage.is_active == True).all(),
        )
    return _cached_json("site-content", _build)


@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    def _build():
        return db.query(SiteSetting).all()
    return _cached_json("settings", _build)


@router.get("/navigation")
def get_navigation(db: Session = Depends(get_db)):
    def _build():
        return db.query(NavigationItem).filter(NavigationItem.is_active == True).order_by(NavigationItem.sort_order).all()
    return _cached_json("navigation", _build)


@router.get("/carousel")
def get_carousel(db: Session = Depends(get_db)):
    def _build():
        return db.query(CarouselSlide).filter(CarouselSlide.is_active == True).order_by(CarouselSlide.sort_order).all()
    return _cached_json("carousel", _build)


@router.get("/page-contents")
def get_page_contents(page_key: Optional[str] = Query(None), db: Session = Depends(get_db)):
    cache_key = f"page-contents:{page_key or 'all'}"
    def _build():
        q = db.query(PageContent).filter(PageContent.is_active == True)
        if page_key:
            q = q.filter(PageContent.page_key == page_key)
        return q.order_by(PageContent.sort_order).all()
    return _cached_json(cache_key, _build)


@router.get("/services")
def get_services(db: Session = Depends(get_db)):
    def _build():
        return db.query(Service).filter(Service.is_active == True).order_by(Service.sort_order).all()
    return _cached_json("services", _build)


@router.get("/sectors")
def get_sectors(db: Session = Depends(get_db)):
    def _build():
        return db.query(Sector).filter(Sector.is_active == True).order_by(Sector.sort_order).all()
    return _cached_json("sectors", _build)


@router.get("/team")
def get_team(db: Session = Depends(get_db)):
    def _build():
        return db.query(TeamMember).filter(TeamMember.is_active == True).order_by(TeamMember.sort_order).all()
    return _cached_json("team", _build)


@router.get("/countries")
def get_countries(db: Session = Depends(get_db)):
    def _build():
        return db.query(Country).filter(Country.is_active == True).order_by(Country.sort_order).all()
    return _cached_json("countries", _build)


@router.get("/countries/{slug}")
def get_country_by_slug(slug: str, db: Session = Depends(get_db)):
    cache_key = f"country:{slug}"
    def _build():
        country = db.query(Country).filter(Country.slug == slug, Country.is_active == True).first()
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        return country
    return _cached_json(cache_key, _build)


@router.get("/contact-info")
def get_contact_info(country_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    cache_key = f"contact-info:{country_id or 'all'}"
    def _build():
        q = db.query(ContactInfo).filter(ContactInfo.is_active == True)
        if country_id:
            q = q.filter(ContactInfo.country_id == country_id)
        return q.all()
    return _cached_json(cache_key, _build)


@router.get("/social-links")
def get_social_links(db: Session = Depends(get_db)):
    def _build():
        return db.query(SocialLink).filter(SocialLink.is_active == True).order_by(SocialLink.sort_order).all()
    return _cached_json("social-links", _build)


@router.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    def _build():
        return db.query(Brand).filter(Brand.is_active == True).order_by(Brand.sort_order).all()
    return _cached_json("brands", _build)


@router.get("/products")
def get_products(category: Optional[str] = Query(None), db: Session = Depends(get_db)):
    cache_key = f"products:{category or 'all'}"
    def _build():
        q = db.query(Product).filter(Product.is_active == True)
        if category:
            q = q.join(ProductCategory, Product.category_id == ProductCategory.id).filter(
                ProductCategory.slug == category
            )
        items = q.order_by(Product.sort_order).all()
        return [ProductOut.model_validate(p) for p in items]
    return _cached_json(cache_key, _build)


@router.get("/products/{slug}")
def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    cache_key = f"product:{slug}"
    def _build():
        product = db.query(Product).filter(Product.slug == slug, Product.is_active == True).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductOut.model_validate(product)
    return _cached_json(cache_key, _build)


@router.get("/product-categories")
def get_product_categories(db: Session = Depends(get_db)):
    def _build():
        cats = db.query(ProductCategory).filter(ProductCategory.is_active == True).order_by(ProductCategory.sort_order).all()
        return [ProductCategoryOut.model_validate(c) for c in cats]
    return _cached_json("product-categories", _build)


@router.get("/product-categories/{slug}")
def get_product_category_by_slug(slug: str, db: Session = Depends(get_db)):
    cache_key = f"product-category:{slug}"
    def _build():
        cat = db.query(ProductCategory).filter(ProductCategory.slug == slug, ProductCategory.is_active == True).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        products = db.query(Product).filter(
            Product.category_id == cat.id, Product.is_active == True
        ).order_by(Product.sort_order).all()
        return {
            "category": ProductCategoryOut.model_validate(cat).model_dump(mode="json"),
            "products": [ProductOut.model_validate(p).model_dump(mode="json") for p in products],
        }
    return _cached_json(cache_key, _build)


# ---------------------------------------------------------------------------
# Search — exact match jumps straight to the page, else returns a ranked list
# ---------------------------------------------------------------------------

def _norm(s: Optional[str]) -> str:
    """Normalize a search token: lowercase, drop spaces / dashes / underscores."""
    if not s:
        return ""
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _product_url(p: Product) -> str:
    cat_slug = p.category.slug if p.category else "all"
    return f"/products/{cat_slug}/{p.slug}"


@router.get("/search")
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    cache_key = f"search:{_norm(q)}"

    def _build():
        nq = _norm(q)

        # 1) Admin-managed alias exact match -> redirect
        for alias in db.query(SearchAlias).filter(SearchAlias.is_active == True).all():
            if _norm(alias.keyword) == nq and alias.is_redirect:
                url = alias.target_url
                if not url:
                    if alias.target_type == "category":
                        url = f"/products/{alias.target_slug}"
                    else:
                        prod = db.query(Product).filter(Product.slug == alias.target_slug).first()
                        url = _product_url(prod) if prod else f"/products"
                return {"redirect": url}

        # 2) Exact model code -> straight to product page
        for p in db.query(Product).filter(Product.is_active == True).all():
            if _norm(p.model_code) == nq or _norm(p.slug) == nq or _norm(p.name_en) == nq:
                return {"redirect": _product_url(p)}

        # 3) Exact category -> straight to category page
        for c in db.query(ProductCategory).filter(ProductCategory.is_active == True).all():
            if _norm(c.slug) == nq or _norm(c.name_en) == nq:
                return {"redirect": f"/products/{c.slug}"}

        # 4) Otherwise -> ranked partial results
        like = f"%{q.strip()}%"
        prod_q = db.query(Product).filter(
            Product.is_active == True,
            (Product.name_en.ilike(like))
            | (Product.model_code.ilike(like))
            | (Product.seo_keywords.ilike(like)),
        ).order_by(Product.sort_order).limit(40).all()

        cat_q = db.query(ProductCategory).filter(
            ProductCategory.is_active == True,
            (ProductCategory.name_en.ilike(like))
            | (ProductCategory.seo_keywords.ilike(like)),
        ).order_by(ProductCategory.sort_order).limit(20).all()

        return {
            "redirect": None,
            "query": q,
            "categories": [
                {
                    "slug": c.slug,
                    "name_en": c.name_en,
                    "image_url": c.image_url,
                    "url": f"/products/{c.slug}",
                }
                for c in cat_q
            ],
            "products": [
                {
                    "slug": p.slug,
                    "model_code": p.model_code,
                    "name_en": p.name_en,
                    "image_url": p.image_url,
                    "category": p.category.name_en if p.category else None,
                    "url": _product_url(p),
                }
                for p in prod_q
            ],
        }

    return _cached_json(cache_key, _build)


@router.get("/banners")
def get_banners(country_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    cache_key = f"banners:{country_id or 'all'}"
    def _build():
        q = db.query(Banner).filter(Banner.is_active == True)
        if country_id:
            q = q.filter(Banner.country_id == country_id)
        return q.order_by(Banner.sort_order).all()
    return _cached_json(cache_key, _build)


@router.get("/project-categories")
def get_project_categories(db: Session = Depends(get_db)):
    def _build():
        return db.query(ProjectCategory).filter(ProjectCategory.is_active == True).order_by(ProjectCategory.sort_order).all()
    return _cached_json("project-categories", _build)


@router.get("/footer-links")
def get_footer_links(db: Session = Depends(get_db)):
    def _build():
        return db.query(FooterLink).filter(FooterLink.is_active == True).order_by(FooterLink.sort_order).all()
    return _cached_json("footer-links", _build)


@router.get("/pages/{slug}")
def get_static_page(slug: str, db: Session = Depends(get_db)):
    cache_key = f"page:{slug}"
    def _build():
        page = db.query(StaticPage).filter(StaticPage.slug == slug, StaticPage.is_active == True).first()
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        return page
    return _cached_json(cache_key, _build)


@router.post("/contact", response_model=ContactSubmissionOut)
def submit_contact_form(
    data: ContactSubmissionCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Save to database
    submission = ContactSubmission(**data.model_dump())
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Resolve notification recipient from settings
    settings_email = db.query(SiteSetting).filter(SiteSetting.key == "notification_email").first()
    recipient = settings_email.value_en if settings_email and settings_email.value_en else None
    
    if recipient:
        # Build email content
        subject = f"New Website Inquiry from {submission.name}"
        if submission.subject:
            subject = f"{submission.subject} (from {submission.name})"
            
        body = f"""
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> {submission.name}</p>
        <p><strong>Email:</strong> {submission.email}</p>
        <p><strong>Phone:</strong> {submission.phone or 'N/A'}</p>
        <p><strong>Subject:</strong> {submission.subject or 'General Inquiry'}</p>
        <p><strong>Message:</strong></p>
        <div style="white-space: pre-wrap; padding: 10px; background: #f4f4f4; border-radius: 4px;">
        {submission.message}
        </div>
        """
        
        # Send in background to keep response fast
        background_tasks.add_task(
            send_email,
            subject=subject,
            body=body,
            to_emails=[recipient],
            html=True
        )

    return submission
