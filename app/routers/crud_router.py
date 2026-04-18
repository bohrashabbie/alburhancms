"""Generic CRUD router factory for simple entities."""
import json
from typing import Type, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db, Base
from app.utils.auth import get_current_user
from app.utils.media import save_upload_and_register_media
from app.utils.cache import invalidates_cache
from app.models.user import User


def create_crud_router(
    prefix: str,
    tags: list,
    model: Type[Base],
    schema_out: Type[BaseModel],
    schema_create: Type[BaseModel],
    schema_update: Type[BaseModel],
    public_read: bool = True,
    order_by: str = "sort_order",
    image_fields: Optional[List[str]] = None,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)
    model_column_names = {c.name for c in model.__table__.columns}
    auto_image_fields = [
        c for c in model_column_names
        if c.endswith("_url") and any(k in c for k in ("image", "logo", "flag", "cover"))
    ]
    allowed_image_fields = image_fields or auto_image_fields
    route_folder = prefix.strip("/").replace("api/", "").replace("/", "-")

    @router.get("", response_model=List[schema_out])
    def list_items(
        active_only: bool = Query(True),
        db: Session = Depends(get_db),
    ):
        q = db.query(model)
        if active_only and hasattr(model, "is_active"):
            q = q.filter(model.is_active == True)
        if hasattr(model, order_by):
            q = q.order_by(getattr(model, order_by))
        return q.all()

    @router.get("/{item_id}", response_model=schema_out)
    def get_item(item_id: int, db: Session = Depends(get_db)):
        item = db.query(model).filter(model.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    @router.post("", response_model=schema_out)
    @invalidates_cache
    def create_item(
        data: schema_create,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        item = model(**data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    if allowed_image_fields:
        @router.post("/with-image", response_model=schema_out)
        @invalidates_cache
        async def create_item_with_image(
            payload: str = Form(...),
            file: UploadFile = File(...),
            field: str = Form("image_url"),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
        ):
            if field not in allowed_image_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image field '{field}'. Allowed: {allowed_image_fields}",
                )
            try:
                payload_dict = json.loads(payload)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="`payload` must be valid JSON")

            validated = schema_create.model_validate(payload_dict)
            media = await save_upload_and_register_media(
                file=file,
                db=db,
                current_user=current_user,
                folder=route_folder,
            )
            values = validated.model_dump()
            values[field] = media.file_path
            item = model(**values)
            db.add(item)
            db.commit()
            db.refresh(item)
            return item

    @router.put("/{item_id}", response_model=schema_out)
    @invalidates_cache
    def update_item(
        item_id: int,
        data: schema_update,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        item = db.query(model).filter(model.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    if allowed_image_fields:
        @router.post("/{item_id}/upload-image", response_model=schema_out)
        @invalidates_cache
        async def upload_item_image(
            item_id: int,
            file: UploadFile = File(...),
            field: str = Query("image_url"),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
        ):
            if field not in allowed_image_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image field '{field}'. Allowed: {allowed_image_fields}",
                )
            item = db.query(model).filter(model.id == item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")

            media = await save_upload_and_register_media(
                file=file,
                db=db,
                current_user=current_user,
                folder=route_folder,
            )
            setattr(item, field, media.file_path)
            db.commit()
            db.refresh(item)
            return item

    @router.delete("/{item_id}")
    @invalidates_cache
    def delete_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        item = db.query(model).filter(model.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(item)
        db.commit()
        return {"detail": "Item deleted"}

    return router
