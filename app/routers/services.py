from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.service import Service, ServiceItem
from app.models.user import User
from app.schemas.schemas import (
    ServiceOut, ServiceCreate, ServiceUpdate,
    ServiceItemOut, ServiceItemCreate,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("", response_model=List[ServiceOut])
def list_services(active_only: bool = Query(True), db: Session = Depends(get_db)):
    q = db.query(Service)
    if active_only:
        q = q.filter(Service.is_active == True)
    return q.order_by(Service.sort_order).all()


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return svc


@router.post("", response_model=ServiceOut)
def create_service(data: ServiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items_data = data.items
    svc_data = data.model_dump(exclude={"items"})
    svc = Service(**svc_data)
    db.add(svc)
    db.flush()
    for item in items_data:
        db.add(ServiceItem(service_id=svc.id, **item.model_dump()))
    db.commit()
    db.refresh(svc)
    return svc


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(service_id: int, data: ServiceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(svc, key, value)
    db.commit()
    db.refresh(svc)
    return svc


@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(svc)
    db.commit()
    return {"detail": "Service deleted"}


# Service Items sub-routes
@router.get("/{service_id}/items", response_model=List[ServiceItemOut])
def list_service_items(service_id: int, db: Session = Depends(get_db)):
    return db.query(ServiceItem).filter(ServiceItem.service_id == service_id).order_by(ServiceItem.sort_order).all()


@router.post("/{service_id}/items", response_model=ServiceItemOut)
def add_service_item(service_id: int, data: ServiceItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    item = ServiceItem(service_id=service_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=ServiceItemOut)
def update_service_item(item_id: int, data: ServiceItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(ServiceItem).filter(ServiceItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Service item not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}")
def delete_service_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(ServiceItem).filter(ServiceItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Service item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Service item deleted"}
