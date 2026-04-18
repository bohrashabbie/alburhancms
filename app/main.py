import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import engine, Base
from app.models import *  # noqa: F401, F403 - import all models to register them
from app.routers import auth, services, projects, public, contact_submissions, media
from app.routers.crud_router import create_crud_router
from app.models.site_settings import SiteSetting
from app.models.navigation import NavigationItem
from app.models.carousel import CarouselSlide
from app.models.page_content import PageContent
from app.models.sector import Sector
from app.models.team_member import TeamMember
from app.models.country import Country
from app.models.branch import Branch
from app.models.contact_info import ContactInfo
from app.models.social_link import SocialLink
from app.models.brand import Brand
from app.models.product import Product
from app.models.banner import Banner
from app.models.static_page import StaticPage
from app.models.footer_link import FooterLink
from app.schemas.schemas import (
    SiteSettingOut, SiteSettingCreate, SiteSettingUpdate,
    NavigationItemOut, NavigationItemCreate, NavigationItemUpdate,
    CarouselSlideOut, CarouselSlideCreate, CarouselSlideUpdate,
    PageContentOut, PageContentCreate, PageContentUpdate,
    SectorOut, SectorCreate, SectorUpdate,
    TeamMemberOut, TeamMemberCreate, TeamMemberUpdate,
    CountryOut, CountryCreate, CountryUpdate,
    BranchOut, BranchCreate, BranchUpdate,
    ContactInfoOut, ContactInfoCreate, ContactInfoUpdate,
    SocialLinkOut, SocialLinkCreate, SocialLinkUpdate,
    BrandOut, BrandCreate, BrandUpdate,
    ProductOut, ProductCreate, ProductUpdate,
    BannerOut, BannerCreate, BannerUpdate,
    StaticPageOut, StaticPageCreate, StaticPageUpdate,
    FooterLinkOut, FooterLinkCreate, FooterLinkUpdate,
)

settings = get_settings()

app = FastAPI(
    title="AL-Burhan CMS API",
    description="Content Management System API for AL-Burhan Regional Website",
    version="1.0.0",
)

# CORS - allow all origins for public API access
origins = ["*"] if settings.CORS_ORIGINS == "*" else [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False if origins == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Create tables
Base.metadata.create_all(bind=engine)

# ---- Register Routers ----
# Auth & specialized routers
app.include_router(auth.router)
app.include_router(services.router)
app.include_router(projects.router)
app.include_router(public.router)
app.include_router(contact_submissions.router)
app.include_router(media.router)

# Generic CRUD routers for all simple entities
app.include_router(create_crud_router("/api/site-settings", ["Site Settings"], SiteSetting, SiteSettingOut, SiteSettingCreate, SiteSettingUpdate))
app.include_router(create_crud_router("/api/navigation", ["Navigation"], NavigationItem, NavigationItemOut, NavigationItemCreate, NavigationItemUpdate))
app.include_router(create_crud_router("/api/carousel", ["Carousel"], CarouselSlide, CarouselSlideOut, CarouselSlideCreate, CarouselSlideUpdate))
app.include_router(create_crud_router("/api/page-contents", ["Page Contents"], PageContent, PageContentOut, PageContentCreate, PageContentUpdate))
app.include_router(create_crud_router("/api/sectors", ["Sectors"], Sector, SectorOut, SectorCreate, SectorUpdate))
app.include_router(create_crud_router("/api/team-members", ["Team Members"], TeamMember, TeamMemberOut, TeamMemberCreate, TeamMemberUpdate))
app.include_router(create_crud_router("/api/countries", ["Countries"], Country, CountryOut, CountryCreate, CountryUpdate))
app.include_router(create_crud_router("/api/branches", ["Branches"], Branch, BranchOut, BranchCreate, BranchUpdate))
app.include_router(create_crud_router("/api/contact-info", ["Contact Info"], ContactInfo, ContactInfoOut, ContactInfoCreate, ContactInfoUpdate, order_by="id"))
app.include_router(create_crud_router("/api/social-links", ["Social Links"], SocialLink, SocialLinkOut, SocialLinkCreate, SocialLinkUpdate))
app.include_router(create_crud_router("/api/brands", ["Brands"], Brand, BrandOut, BrandCreate, BrandUpdate))
app.include_router(create_crud_router("/api/products", ["Products"], Product, ProductOut, ProductCreate, ProductUpdate))
app.include_router(create_crud_router("/api/banners", ["Banners"], Banner, BannerOut, BannerCreate, BannerUpdate))
app.include_router(create_crud_router("/api/static-pages", ["Static Pages"], StaticPage, StaticPageOut, StaticPageCreate, StaticPageUpdate, order_by="id"))
app.include_router(create_crud_router("/api/footer-links", ["Footer Links"], FooterLink, FooterLinkOut, FooterLinkCreate, FooterLinkUpdate))


@app.get("/")
def root():
    return {"message": "AL-Burhan CMS API", "docs": "/docs"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
