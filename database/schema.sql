-- AL-Burhan CMS Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS (Admin Panel Authentication)
-- ============================================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'editor', -- admin, editor
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SITE SETTINGS (Global key-value config)
-- ============================================================================
CREATE TABLE site_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value_en TEXT,
    value_ar TEXT,
    setting_type VARCHAR(50) DEFAULT 'text', -- text, image, url, json
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- NAVIGATION ITEMS
-- ============================================================================
CREATE TABLE navigation_items (
    id SERIAL PRIMARY KEY,
    label_en VARCHAR(255) NOT NULL,
    label_ar VARCHAR(255),
    href VARCHAR(255) NOT NULL,
    icon VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    parent_id INTEGER REFERENCES navigation_items(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CAROUSEL SLIDES
-- ============================================================================
CREATE TABLE carousel_slides (
    id SERIAL PRIMARY KEY,
    title_en VARCHAR(255),
    title_ar VARCHAR(255),
    subtitle_en VARCHAR(255),
    subtitle_ar VARCHAR(255),
    description_en TEXT,
    description_ar TEXT,
    image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PAGE CONTENTS (Flexible content blocks for any page/section)
-- ============================================================================
CREATE TABLE page_contents (
    id SERIAL PRIMARY KEY,
    page_key VARCHAR(100) NOT NULL,       -- home, about, contact, etc.
    section_key VARCHAR(100) NOT NULL,     -- hero, introduction, vision, mission, etc.
    title_en VARCHAR(500),
    title_ar VARCHAR(500),
    content_en TEXT,
    content_ar TEXT,
    extra_data JSONB DEFAULT '{}',         -- for additional fields
    image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(page_key, section_key)
);

-- ============================================================================
-- SERVICES
-- ============================================================================
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    title_en VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    description_en TEXT,
    description_ar TEXT,
    image_url VARCHAR(500),
    icon VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE service_items (
    id SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    text_en VARCHAR(500) NOT NULL,
    text_ar VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SECTORS
-- ============================================================================
CREATE TABLE sectors (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    icon VARCHAR(100),
    description_en TEXT,
    description_ar TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- TEAM MEMBERS (Owners / Founders)
-- ============================================================================
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    designation_en VARCHAR(255),
    designation_ar VARCHAR(255),
    quote_en TEXT,
    quote_ar TEXT,
    image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- COUNTRIES
-- ============================================================================
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    slug VARCHAR(100) UNIQUE NOT NULL,        -- kuwait, uae, china, egypt
    firm_name_en VARCHAR(255),
    firm_name_ar VARCHAR(255),
    description_en TEXT,
    description_ar TEXT,
    flag_url VARCHAR(500),
    country_image_url VARCHAR(500),
    logo_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- BRANCHES (Per country)
-- ============================================================================
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    country_id INTEGER NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    name_en VARCHAR(255),
    name_ar VARCHAR(255),
    address_en TEXT,
    address_ar TEXT,
    phone1 VARCHAR(50),
    phone2 VARCHAR(50),
    email VARCHAR(255),
    map_lat DECIMAL(10, 8),
    map_lng DECIMAL(11, 8),
    is_head_office BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CONTACT INFO (Detailed per-country contact)
-- ============================================================================
CREATE TABLE contact_info (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES countries(id) ON DELETE SET NULL,
    company_name_en VARCHAR(255),
    company_name_ar VARCHAR(255),
    office_en VARCHAR(255),
    office_ar VARCHAR(255),
    floor_en VARCHAR(255),
    floor_ar VARCHAR(255),
    area_en VARCHAR(255),
    area_ar VARCHAR(255),
    city_en VARCHAR(255),
    city_ar VARCHAR(255),
    address_en TEXT,
    address_ar TEXT,
    district_en VARCHAR(255),
    district_ar VARCHAR(255),
    province_en VARCHAR(255),
    province_ar VARCHAR(255),
    postal_code VARCHAR(50),
    phone1 VARCHAR(50),
    phone2 VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    business_hours_en VARCHAR(255),
    business_hours_ar VARCHAR(255),
    is_head_office BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SOCIAL LINKS
-- ============================================================================
CREATE TABLE social_links (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(100) NOT NULL,      -- facebook, twitter, instagram, linkedin
    url VARCHAR(500) NOT NULL,
    icon VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- BRANDS (Partner brands)
-- ============================================================================
CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PRODUCTS
-- ============================================================================
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description_en TEXT,
    description_ar TEXT,
    image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- BANNERS
-- ============================================================================
CREATE TABLE banners (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES countries(id) ON DELETE SET NULL,
    name_en VARCHAR(255),
    name_ar VARCHAR(255),
    description_en TEXT,
    description_ar TEXT,
    image_url VARCHAR(500),
    banner_type VARCHAR(100),
    position VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PROJECT CATEGORIES
-- ============================================================================
CREATE TABLE project_categories (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    cover_image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PROJECTS
-- ============================================================================
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES project_categories(id) ON DELETE SET NULL,
    country_id INTEGER REFERENCES countries(id) ON DELETE SET NULL,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description_en TEXT,
    description_ar TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PROJECT IMAGES
-- ============================================================================
CREATE TABLE project_images (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- STATIC PAGES (privacy, terms, cookies, etc.)
-- ============================================================================
CREATE TABLE static_pages (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title_en VARCHAR(255),
    title_ar VARCHAR(255),
    content_en TEXT,
    content_ar TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CONTACT FORM SUBMISSIONS
-- ============================================================================
CREATE TABLE contact_submissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    subject VARCHAR(500),
    message TEXT,
    country_id INTEGER REFERENCES countries(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- FOOTER LINKS
-- ============================================================================
CREATE TABLE footer_links (
    id SERIAL PRIMARY KEY,
    section VARCHAR(100) NOT NULL,      -- services, legal
    label_en VARCHAR(255) NOT NULL,
    label_ar VARCHAR(255),
    href VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MEDIA FILES (uploaded via admin)
-- ============================================================================
CREATE TABLE media_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    original_name VARCHAR(500),
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(100),
    file_size INTEGER,
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_page_contents_page_key ON page_contents(page_key);
CREATE INDEX idx_page_contents_section_key ON page_contents(section_key);
CREATE INDEX idx_branches_country_id ON branches(country_id);
CREATE INDEX idx_contact_info_country_id ON contact_info(country_id);
CREATE INDEX idx_projects_category_id ON projects(category_id);
CREATE INDEX idx_projects_country_id ON projects(country_id);
CREATE INDEX idx_project_images_project_id ON project_images(project_id);
CREATE INDEX idx_banners_country_id ON banners(country_id);
CREATE INDEX idx_service_items_service_id ON service_items(service_id);
CREATE INDEX idx_contact_submissions_is_read ON contact_submissions(is_read);

-- ============================================================================
-- TRIGGER: auto-update updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT table_name FROM information_schema.columns
        WHERE column_name = 'updated_at'
        AND table_schema = 'public'
    LOOP
        EXECUTE format('
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        ', t, t);
    END LOOP;
END;
$$;

-- ============================================================================
-- DEFAULT ADMIN USER (password: admin123 - CHANGE IN PRODUCTION)
-- ============================================================================
INSERT INTO users (username, email, password_hash, full_name, role)
VALUES ('admin', 'admin@alburhan-regional.com',
    '$2b$12$LJ3m4ys3Gzf0dOCP5gUMYeVpOYPHbKXPFDREOlr2ot6k2.Wd0BCWK',
    'Admin', 'admin');
