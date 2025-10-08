from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User, Store
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse, StoreListResponse

router = APIRouter(prefix="/stores", tags=["stores"])

@router.get("/", response_model=StoreListResponse)
def get_stores(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Store)
    
    if current_user.type == "store":
        query = query.filter(Store.owner_id == current_user.id)
    
    if search:
        query = query.filter(
            or_(
                Store.name.ilike(f"%{search}%"),
                Store.description.ilike(f"%{search}%")
            )
        )
    
    if city:
        query = query.filter(Store.city == city)
    
    if sector:
        query = query.filter(Store.sector == sector)
    
    total = query.count()
    stores = query.offset((page - 1) * limit).limit(limit).all()
    
    store_responses = []
    for store in stores:
        store_dict = store.__dict__.copy()
        store_dict["products"] = store.products.split(",") if store.products else []
        if store_dict.get("image"):
            store_dict["image"] = f"/static/{store_dict['image']}"
        store_responses.append(StoreResponse(**store_dict))
    
    return StoreListResponse(
        stores=store_responses,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if current_user.type == "store" and store.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    store_dict = store.__dict__.copy()
    store_dict["products"] = store.products.split(",") if store.products else []
    if store_dict.get("image"):
        store_dict["image"] = f"/static/{store_dict['image']}"
    return StoreResponse(**store_dict)

@router.post("/", response_model=StoreResponse)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.type == "store":
        existing_store = db.query(Store).filter(Store.owner_id == current_user.id).first()
        if existing_store:
            raise HTTPException(
                status_code=400,
                detail="Store owners can only have one store"
            )
    
    store_data = store.dict()
    products_str = ",".join(store_data.pop("products", []))
    
    db_store = Store(
        **store_data,
        products=products_str,
        owner_id=current_user.id
    )
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    
    store_dict = db_store.__dict__.copy()
    store_dict["products"] = db_store.products.split(",") if db_store.products else []
    if store_dict.get("image"):
        store_dict["image"] = f"/static/{store_dict['image']}"
    return StoreResponse(**store_dict)

@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: str,
    store_update: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if current_user.type == "store" and store.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = store_update.dict(exclude_unset=True)
    if "products" in update_data:
        update_data["products"] = ",".join(update_data["products"])
    
    for field, value in update_data.items():
        setattr(store, field, value)
    
    db.commit()
    db.refresh(store)
    
    store_dict = store.__dict__.copy()
    store_dict["products"] = store.products.split(",") if store.products else []
    if store_dict.get("image"):
        store_dict["image"] = f"/static/{store_dict['image']}"
    return StoreResponse(**store_dict)

@router.delete("/{store_id}")
def delete_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if current_user.type == "store" and store.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(store)
    db.commit()
    return {"message": "Store deleted successfully"}
