from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User, Offer, Store
from app.schemas.offer import OfferCreate, OfferUpdate, OfferResponse, OfferListResponse

router = APIRouter(prefix="/offers", tags=["offers"])

@router.get("/", response_model=OfferListResponse)
def get_offers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    store_id: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Offer)
    
    if current_user.type == "store":
        user_stores = db.query(Store).filter(Store.owner_id == current_user.id).all()
        store_ids = [store.id for store in user_stores]
        query = query.filter(Offer.store_id.in_(store_ids))
    
    if store_id:
        query = query.filter(Offer.store_id == store_id)
    
    if active_only:
        query = query.filter(Offer.is_active == True)
    
    if search:
        query = query.filter(
            or_(
                Offer.title.ilike(f"%{search}%"),
                Offer.description.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    offers = query.offset((page - 1) * limit).limit(limit).all()
    
    offer_responses = []
    for offer in offers:
        offer_dict = OfferResponse.from_orm(offer).dict()
        store = db.query(Store).filter(Store.id == offer.store_id).first()
        offer_dict["store_name"] = store.name if store else None
        offer_responses.append(OfferResponse(**offer_dict))
    
    return OfferListResponse(
        offers=offer_responses,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(
    offer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if current_user.type == "store":
        store = db.query(Store).filter(Store.id == offer.store_id).first()
        if not store or store.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    offer_dict = OfferResponse.from_orm(offer).dict()
    store = db.query(Store).filter(Store.id == offer.store_id).first()
    offer_dict["store_name"] = store.name if store else None
    
    return OfferResponse(**offer_dict)

@router.post("/", response_model=OfferResponse)
def create_offer(
    offer: OfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    store = db.query(Store).filter(Store.id == offer.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if current_user.type == "store" and store.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_offer = Offer(**offer.dict())
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    
    offer_dict = OfferResponse.from_orm(db_offer).dict()
    offer_dict["store_name"] = store.name
    return OfferResponse(**offer_dict)

@router.put("/{offer_id}", response_model=OfferResponse)
def update_offer(
    offer_id: str,
    offer_update: OfferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if current_user.type == "store":
        store = db.query(Store).filter(Store.id == offer.store_id).first()
        if not store or store.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = offer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(offer, field, value)
    
    db.commit()
    db.refresh(offer)
    
    offer_dict = OfferResponse.from_orm(offer).dict()
    store = db.query(Store).filter(Store.id == offer.store_id).first()
    offer_dict["store_name"] = store.name if store else None
    
    return OfferResponse(**offer_dict)

@router.delete("/{offer_id}")
def delete_offer(
    offer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if current_user.type == "store":
        store = db.query(Store).filter(Store.id == offer.store_id).first()
        if not store or store.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(offer)
    db.commit()
    return {"message": "Offer deleted successfully"}
