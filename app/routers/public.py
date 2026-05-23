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
)
from app.schemas.schemas import (
    FullSiteContentOut, ContactSubmissionCreate, ContactSubmissionOut,
    SiteSettingOut, NavigationItemOut, CarouselSlideOut, PageContentOut,
    ServiceOut, SectorOut, TeamMemberOut, CountryOut, ContactInfoOut,
    SocialLinkOut, BrandOut, ProductOut, BannerOut, ProjectCategoryOut,
    FooterLinkOut, StaticPageOut,
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
def get_products(db: Session = Depends(get_db)):
    def _build():
        return db.query(Product).filter(Product.is_active == True).order_by(Product.sort_order).all()
    return _cached_json("products", _build)


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
