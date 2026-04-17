from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# ============================================================================
# AUTH
# ============================================================================
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "editor"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


# ============================================================================
# SITE SETTINGS
# ============================================================================
class SiteSettingOut(BaseModel):
    id: int
    key: str
    value_en: Optional[str] = None
    value_ar: Optional[str] = None
    setting_type: Optional[str] = None
    description: Optional[str] = None
    class Config:
        from_attributes = True

class SiteSettingCreate(BaseModel):
    key: str
    value_en: Optional[str] = None
    value_ar: Optional[str] = None
    setting_type: str = "text"
    description: Optional[str] = None

class SiteSettingUpdate(BaseModel):
    value_en: Optional[str] = None
    value_ar: Optional[str] = None
    setting_type: Optional[str] = None
    description: Optional[str] = None


# ============================================================================
# NAVIGATION
# ============================================================================
class NavigationItemOut(BaseModel):
    id: int
    label_en: str
    label_ar: Optional[str] = None
    href: str
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    parent_id: Optional[int] = None
    class Config:
        from_attributes = True

class NavigationItemCreate(BaseModel):
    label_en: str
    label_ar: Optional[str] = None
    href: str
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    parent_id: Optional[int] = None

class NavigationItemUpdate(BaseModel):
    label_en: Optional[str] = None
    label_ar: Optional[str] = None
    href: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None


# ============================================================================
# CAROUSEL SLIDES
# ============================================================================
class CarouselSlideOut(BaseModel):
    id: int
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    subtitle_en: Optional[str] = None
    subtitle_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class CarouselSlideCreate(BaseModel):
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    subtitle_en: Optional[str] = None
    subtitle_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class CarouselSlideUpdate(BaseModel):
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    subtitle_en: Optional[str] = None
    subtitle_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# PAGE CONTENTS
# ============================================================================
class PageContentOut(BaseModel):
    id: int
    page_key: str
    section_key: str
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    content_en: Optional[str] = None
    content_ar: Optional[str] = None
    extra_data: Optional[Any] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class PageContentCreate(BaseModel):
    page_key: str
    section_key: str
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    content_en: Optional[str] = None
    content_ar: Optional[str] = None
    extra_data: Optional[dict] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class PageContentUpdate(BaseModel):
    page_key: Optional[str] = None
    section_key: Optional[str] = None
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    content_en: Optional[str] = None
    content_ar: Optional[str] = None
    extra_data: Optional[dict] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# SERVICES
# ============================================================================
class ServiceItemOut(BaseModel):
    id: int
    service_id: int
    text_en: str
    text_ar: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class ServiceItemCreate(BaseModel):
    text_en: str
    text_ar: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class ServiceOut(BaseModel):
    id: int
    title_en: str
    title_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    items: List[ServiceItemOut] = []
    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    title_en: str
    title_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    items: List[ServiceItemCreate] = []

class ServiceUpdate(BaseModel):
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# SECTORS
# ============================================================================
class SectorOut(BaseModel):
    id: int
    name_en: str
    name_ar: Optional[str] = None
    icon: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class SectorCreate(BaseModel):
    name_en: str
    name_ar: Optional[str] = None
    icon: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class SectorUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    icon: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# TEAM MEMBERS
# ============================================================================
class TeamMemberOut(BaseModel):
    id: int
    name_en: str
    name_ar: Optional[str] = None
    designation_en: Optional[str] = None
    designation_ar: Optional[str] = None
    quote_en: Optional[str] = None
    quote_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class TeamMemberCreate(BaseModel):
    name_en: str
    name_ar: Optional[str] = None
    designation_en: Optional[str] = None
    designation_ar: Optional[str] = None
    quote_en: Optional[str] = None
    quote_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class TeamMemberUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    designation_en: Optional[str] = None
    designation_ar: Optional[str] = None
    quote_en: Optional[str] = None
    quote_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# COUNTRIES
# ============================================================================
class BranchOut(BaseModel):
    id: int
    country_id: int
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    address_en: Optional[str] = None
    address_ar: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None
    map_lat: Optional[float] = None
    map_lng: Optional[float] = None
    is_head_office: bool = False
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class BranchCreate(BaseModel):
    country_id: int
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    address_en: Optional[str] = None
    address_ar: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None
    map_lat: Optional[float] = None
    map_lng: Optional[float] = None
    is_head_office: bool = False
    sort_order: int = 0
    is_active: bool = True

class BranchUpdate(BaseModel):
    country_id: Optional[int] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    address_en: Optional[str] = None
    address_ar: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None
    map_lat: Optional[float] = None
    map_lng: Optional[float] = None
    is_head_office: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class CountryOut(BaseModel):
    id: int
    name_en: str
    name_ar: Optional[str] = None
    slug: str
    firm_name_en: Optional[str] = None
    firm_name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    flag_url: Optional[str] = None
    country_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    branches: List[BranchOut] = []
    class Config:
        from_attributes = True

class CountryCreate(BaseModel):
    name_en: str
    name_ar: Optional[str] = None
    slug: str
    firm_name_en: Optional[str] = None
    firm_name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    flag_url: Optional[str] = None
    country_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class CountryUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    slug: Optional[str] = None
    firm_name_en: Optional[str] = None
    firm_name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    flag_url: Optional[str] = None
    country_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# CONTACT INFO
# ============================================================================
class ContactInfoOut(BaseModel):
    id: int
    country_id: Optional[int] = None
    company_name_en: Optional[str] = None
    company_name_ar: Optional[str] = None
    office_en: Optional[str] = None
    office_ar: Optional[str] = None
    floor_en: Optional[str] = None
    floor_ar: Optional[str] = None
    area_en: Optional[str] = None
    area_ar: Optional[str] = None
    city_en: Optional[str] = None
    city_ar: Optional[str] = None
    address_en: Optional[str] = None
    address_ar: Optional[str] = None
    district_en: Optional[str] = None
    district_ar: Optional[str] = None
    province_en: Optional[str] = None
    province_ar: Optional[str] = None
    postal_code: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    business_hours_en: Optional[str] = None
    business_hours_ar: Optional[str] = None
    is_head_office: bool = False
    is_active: bool = True
    class Config:
        from_attributes = True

class ContactInfoCreate(BaseModel):
    country_id: Optional[int] = None
    company_name_en: Optional[str] = None
    company_name_ar: Optional[str] = None
    office_en: Optional[str] = None
    office_ar: Optional[str] = None
    floor_en: Optional[str] = None
    floor_ar: Optional[str] = None
    area_en: Optional[str] = None
    area_ar: Optional[str] = None
    city_en: Optional[str] = None
    city_ar: Optional[str] = None
    address_en: Optional[str] = None
    address_ar: Optional[str] = None
    district_en: Optional[str] = None
    district_ar: Optional[str] = None
    province_en: Optional[str] = None
    province_ar: Optional[str] = None
    postal_code: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    business_hours_en: Optional[str] = None
    business_hours_ar: Optional[str] = None
    is_head_office: bool = False
    is_active: bool = True

class ContactInfoUpdate(ContactInfoCreate):
    pass


# ============================================================================
# SOCIAL LINKS
# ============================================================================
class SocialLinkOut(BaseModel):
    id: int
    platform: str
    url: str
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class SocialLinkCreate(BaseModel):
    platform: str
    url: str
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class SocialLinkUpdate(BaseModel):
    platform: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# BRANDS
# ============================================================================
class BrandOut(BaseModel):
    id: int
    name: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class BrandCreate(BaseModel):
    name: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# PRODUCTS
# ============================================================================
class ProductOut(BaseModel):
    id: int
    name_en: str
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name_en: str
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class ProductUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# BANNERS
# ============================================================================
class BannerOut(BaseModel):
    id: int
    country_id: Optional[int] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    banner_type: Optional[str] = None
    position: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class BannerCreate(BaseModel):
    country_id: Optional[int] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    banner_type: Optional[str] = None
    position: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class BannerUpdate(BaseModel):
    country_id: Optional[int] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    image_url: Optional[str] = None
    banner_type: Optional[str] = None
    position: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# PROJECTS
# ============================================================================
class ProjectImageOut(BaseModel):
    id: int
    project_id: int
    image_url: str
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class ProjectImageCreate(BaseModel):
    image_url: str
    sort_order: int = 0
    is_active: bool = True

class ProjectOut(BaseModel):
    id: int
    category_id: Optional[int] = None
    country_id: Optional[int] = None
    name_en: str
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    images: List[ProjectImageOut] = []
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    category_id: Optional[int] = None
    country_id: Optional[int] = None
    name_en: str
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class ProjectUpdate(BaseModel):
    category_id: Optional[int] = None
    country_id: Optional[int] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class ProjectCategoryOut(BaseModel):
    id: int
    name_en: str
    name_ar: Optional[str] = None
    cover_image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    projects: List[ProjectOut] = []
    class Config:
        from_attributes = True

class ProjectCategoryCreate(BaseModel):
    name_en: str
    name_ar: Optional[str] = None
    cover_image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class ProjectCategoryUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    cover_image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# STATIC PAGES
# ============================================================================
class StaticPageOut(BaseModel):
    id: int
    slug: str
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    content_en: Optional[str] = None
    content_ar: Optional[str] = None
    is_active: bool = True
    class Config:
        from_attributes = True

class StaticPageCreate(BaseModel):
    slug: str
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    content_en: Optional[str] = None
    content_ar: Optional[str] = None
    is_active: bool = True

class StaticPageUpdate(BaseModel):
    slug: Optional[str] = None
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    content_en: Optional[str] = None
    content_ar: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================================
# CONTACT SUBMISSIONS
# ============================================================================
class ContactSubmissionOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    country_id: Optional[int] = None
    is_read: bool = False
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ContactSubmissionCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    country_id: Optional[int] = None


# ============================================================================
# FOOTER LINKS
# ============================================================================
class FooterLinkOut(BaseModel):
    id: int
    section: str
    label_en: str
    label_ar: Optional[str] = None
    href: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    class Config:
        from_attributes = True

class FooterLinkCreate(BaseModel):
    section: str
    label_en: str
    label_ar: Optional[str] = None
    href: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class FooterLinkUpdate(BaseModel):
    section: Optional[str] = None
    label_en: Optional[str] = None
    label_ar: Optional[str] = None
    href: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================================
# MEDIA
# ============================================================================
class MediaFileOut(BaseModel):
    id: int
    filename: str
    original_name: Optional[str] = None
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ============================================================================
# PUBLIC API: Aggregated response for frontend
# ============================================================================
class FullSiteContentOut(BaseModel):
    settings: List[SiteSettingOut] = []
    navigation: List[NavigationItemOut] = []
    carousel_slides: List[CarouselSlideOut] = []
    page_contents: List[PageContentOut] = []
    services: List[ServiceOut] = []
    sectors: List[SectorOut] = []
    team_members: List[TeamMemberOut] = []
    countries: List[CountryOut] = []
    contact_info: List[ContactInfoOut] = []
    social_links: List[SocialLinkOut] = []
    brands: List[BrandOut] = []
    products: List[ProductOut] = []
    banners: List[BannerOut] = []
    project_categories: List[ProjectCategoryOut] = []
    footer_links: List[FooterLinkOut] = []
    static_pages: List[StaticPageOut] = []
