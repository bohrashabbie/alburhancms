"""Public API endpoints for the Next.js frontend - no auth required."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
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

router = APIRouter(prefix="/api/public", tags=["Public API"])


@router.get("/site-content", response_model=FullSiteContentOut)
def get_full_site_content(db: Session = Depends(get_db)):
    """Single endpoint to fetch ALL site content for the frontend."""
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


@router.get("/settings", response_model=List[SiteSettingOut])
def get_settings(db: Session = Depends(get_db)):
    return db.query(SiteSetting).all()


@router.get("/navigation", response_model=List[NavigationItemOut])
def get_navigation(db: Session = Depends(get_db)):
    return db.query(NavigationItem).filter(NavigationItem.is_active == True).order_by(NavigationItem.sort_order).all()


@router.get("/carousel", response_model=List[CarouselSlideOut])
def get_carousel(db: Session = Depends(get_db)):
    return db.query(CarouselSlide).filter(CarouselSlide.is_active == True).order_by(CarouselSlide.sort_order).all()


@router.get("/page-contents", response_model=List[PageContentOut])
def get_page_contents(page_key: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(PageContent).filter(PageContent.is_active == True)
    if page_key:
        q = q.filter(PageContent.page_key == page_key)
    return q.order_by(PageContent.sort_order).all()


@router.get("/services", response_model=List[ServiceOut])
def get_services(db: Session = Depends(get_db)):
    return db.query(Service).filter(Service.is_active == True).order_by(Service.sort_order).all()


@router.get("/sectors", response_model=List[SectorOut])
def get_sectors(db: Session = Depends(get_db)):
    return db.query(Sector).filter(Sector.is_active == True).order_by(Sector.sort_order).all()


@router.get("/team", response_model=List[TeamMemberOut])
def get_team(db: Session = Depends(get_db)):
    return db.query(TeamMember).filter(TeamMember.is_active == True).order_by(TeamMember.sort_order).all()


@router.get("/countries", response_model=List[CountryOut])
def get_countries(db: Session = Depends(get_db)):
    return db.query(Country).filter(Country.is_active == True).order_by(Country.sort_order).all()


@router.get("/countries/{slug}", response_model=CountryOut)
def get_country_by_slug(slug: str, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.slug == slug, Country.is_active == True).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.get("/contact-info", response_model=List[ContactInfoOut])
def get_contact_info(country_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    q = db.query(ContactInfo).filter(ContactInfo.is_active == True)
    if country_id:
        q = q.filter(ContactInfo.country_id == country_id)
    return q.all()


@router.get("/social-links", response_model=List[SocialLinkOut])
def get_social_links(db: Session = Depends(get_db)):
    return db.query(SocialLink).filter(SocialLink.is_active == True).order_by(SocialLink.sort_order).all()


@router.get("/brands", response_model=List[BrandOut])
def get_brands(db: Session = Depends(get_db)):
    return db.query(Brand).filter(Brand.is_active == True).order_by(Brand.sort_order).all()


@router.get("/products", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active == True).order_by(Product.sort_order).all()


@router.get("/banners", response_model=List[BannerOut])
def get_banners(country_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    q = db.query(Banner).filter(Banner.is_active == True)
    if country_id:
        q = q.filter(Banner.country_id == country_id)
    return q.order_by(Banner.sort_order).all()


@router.get("/project-categories", response_model=List[ProjectCategoryOut])
def get_project_categories(db: Session = Depends(get_db)):
    return db.query(ProjectCategory).filter(ProjectCategory.is_active == True).order_by(ProjectCategory.sort_order).all()


@router.get("/footer-links", response_model=List[FooterLinkOut])
def get_footer_links(db: Session = Depends(get_db)):
    return db.query(FooterLink).filter(FooterLink.is_active == True).order_by(FooterLink.sort_order).all()


@router.get("/pages/{slug}", response_model=StaticPageOut)
def get_static_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(StaticPage).filter(StaticPage.slug == slug, StaticPage.is_active == True).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.post("/contact", response_model=ContactSubmissionOut)
def submit_contact_form(data: ContactSubmissionCreate, db: Session = Depends(get_db)):
    submission = ContactSubmission(**data.model_dump())
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
