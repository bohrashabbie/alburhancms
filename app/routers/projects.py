from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import ProjectCategory, Project, ProjectImage
from app.models.user import User
from app.schemas.schemas import (
    ProjectCategoryOut, ProjectCategoryCreate, ProjectCategoryUpdate,
    ProjectOut, ProjectCreate, ProjectUpdate,
    ProjectImageOut, ProjectImageCreate,
)
from app.utils.auth import get_current_user
from app.utils.cache import invalidates_cache
from app.utils.media import save_upload_and_register_media

router = APIRouter(prefix="/api/projects", tags=["Projects"])


# ---- Project Categories ----
@router.get("/categories", response_model=List[ProjectCategoryOut])
def list_categories(active_only: bool = Query(True), db: Session = Depends(get_db)):
    q = db.query(ProjectCategory)
    if active_only:
        q = q.filter(ProjectCategory.is_active == True)
    return q.order_by(ProjectCategory.sort_order).all()


@router.get("/categories/{cat_id}", response_model=ProjectCategoryOut)
def get_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(ProjectCategory).filter(ProjectCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.post("/categories", response_model=ProjectCategoryOut)
@invalidates_cache
def create_category(data: ProjectCategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cat = ProjectCategory(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/categories/{cat_id}", response_model=ProjectCategoryOut)
@invalidates_cache
def update_category(cat_id: int, data: ProjectCategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cat = db.query(ProjectCategory).filter(ProjectCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return cat


@router.post("/categories/{cat_id}/upload-cover", response_model=ProjectCategoryOut)
@invalidates_cache
async def upload_category_cover(
    cat_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = db.query(ProjectCategory).filter(ProjectCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    media = await save_upload_and_register_media(
        file=file,
        db=db,
        current_user=current_user,
        folder="projects-categories",
    )
    cat.cover_image_url = media.file_path
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{cat_id}")
@invalidates_cache
def delete_category(cat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cat = db.query(ProjectCategory).filter(ProjectCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"detail": "Category deleted"}


# ---- Projects ----
@router.get("", response_model=List[ProjectOut])
def list_projects(
    active_only: bool = Query(True),
    country_id: int = Query(None),
    category_id: int = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Project)
    if active_only:
        q = q.filter(Project.is_active == True)
    if country_id:
        q = q.filter(Project.country_id == country_id)
    if category_id:
        q = q.filter(Project.category_id == category_id)
    return q.order_by(Project.sort_order).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj


@router.post("", response_model=ProjectOut)
@invalidates_cache
def create_project(data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = Project(**data.model_dump())
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@router.put("/{project_id}", response_model=ProjectOut)
@invalidates_cache
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(proj, k, v)
    db.commit()
    db.refresh(proj)
    return proj


@router.delete("/{project_id}")
@invalidates_cache
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(proj)
    db.commit()
    return {"detail": "Project deleted"}


# ---- Project Images ----
@router.get("/{project_id}/images", response_model=List[ProjectImageOut])
def list_project_images(project_id: int, db: Session = Depends(get_db)):
    return db.query(ProjectImage).filter(ProjectImage.project_id == project_id).order_by(ProjectImage.sort_order).all()


@router.post("/{project_id}/images", response_model=ProjectImageOut)
@invalidates_cache
def add_project_image(project_id: int, data: ProjectImageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    img = ProjectImage(project_id=project_id, **data.model_dump())
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.post("/{project_id}/images/upload", response_model=ProjectImageOut)
@invalidates_cache
async def upload_project_image(
    project_id: int,
    file: UploadFile = File(...),
    sort_order: int = Form(0),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    media = await save_upload_and_register_media(
        file=file,
        db=db,
        current_user=current_user,
        folder="projects-images",
    )
    img = ProjectImage(
        project_id=project_id,
        image_url=media.file_path,
        sort_order=sort_order,
        is_active=is_active,
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.delete("/images/{image_id}")
@invalidates_cache
def delete_project_image(image_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    img = db.query(ProjectImage).filter(ProjectImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(img)
    db.commit()
    return {"detail": "Image deleted"}
