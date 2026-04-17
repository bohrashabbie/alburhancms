# AL-Burhan CMS API

FastAPI-based Content Management System for the AL-Burhan Regional website.

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env from example
copy .env.example .env
# Edit .env with your database credentials

# Run database schema (optional - tables auto-created on startup)
# psql -h 13.60.4.75 -U postgres -d alburhancms -f database/schema.sql

# Seed the database with static content from frontend
python -m seeds.seed_data

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Endpoints

### Public (No Auth)
- `GET /api/public/site-content` - All site content in one call
- `GET /api/public/settings` - Site settings
- `GET /api/public/navigation` - Navigation items
- `GET /api/public/carousel` - Carousel slides
- `GET /api/public/page-contents?page_key=home` - Page content blocks
- `GET /api/public/services` - Services
- `GET /api/public/sectors` - Sectors
- `GET /api/public/team` - Team members
- `GET /api/public/countries` - Countries with branches
- `GET /api/public/countries/{slug}` - Single country
- `GET /api/public/contact-info` - Contact info
- `GET /api/public/social-links` - Social links
- `GET /api/public/brands` - Brands
- `GET /api/public/products` - Products
- `GET /api/public/banners` - Banners
- `GET /api/public/project-categories` - Project categories with projects
- `GET /api/public/footer-links` - Footer links
- `GET /api/public/pages/{slug}` - Static pages
- `POST /api/public/contact` - Submit contact form

### Admin (Auth Required)
All CRUD endpoints for every entity at `/api/{entity-name}`.

### Auth
- `POST /api/auth/login` - Login (OAuth2 form)
- `GET /api/auth/me` - Current user
- `GET/POST/PUT/DELETE /api/auth/users` - User management (admin only)
