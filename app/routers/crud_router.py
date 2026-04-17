"""Generic CRUD router factory for simple entities."""
from typing import Type, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db, Base
from app.utils.auth import get_current_user
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
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

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

    @router.put("/{item_id}", response_model=schema_out)
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

    @router.delete("/{item_id}")
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
