from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User, Store, Offer
from app.schemas import DashboardStats
from app.schemas.store import StoreResponse
from app.schemas.offer import OfferResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.type == "store":
        user_stores = db.query(Store).filter(Store.owner_id == current_user.id).all()
        store_ids = [store.id for store in user_stores]
        
        total_stores = len(user_stores)
        active_stores = len([s for s in user_stores if s.is_active])
        
        total_offers = db.query(Offer).filter(Offer.store_id.in_(store_ids)).count()
        active_offers = db.query(Offer).filter(
            Offer.store_id.in_(store_ids),
            Offer.is_active == True
        ).count()
        
        recent_stores = user_stores[-5:] if len(user_stores) > 5 else user_stores
        recent_offers = db.query(Offer).filter(
            Offer.store_id.in_(store_ids)
        ).order_by(Offer.created_at.desc()).limit(5).all()
    else:
        total_stores = db.query(Store).count()
        active_stores = db.query(Store).filter(Store.is_active == True).count()
        total_offers = db.query(Offer).count()
        active_offers = db.query(Offer).filter(Offer.is_active == True).count()
        
        recent_stores = db.query(Store).order_by(Store.created_at.desc()).limit(5).all()
        recent_offers = db.query(Offer).order_by(Offer.created_at.desc()).limit(5).all()
    
    store_responses = []
    for store in recent_stores:
        store_dict = StoreResponse.from_orm(store).dict()
        store_dict["products"] = store.products.split(",") if store.products else []
        store_responses.append(StoreResponse(**store_dict))
    
    return DashboardStats(
        total_stores=total_stores,
        active_stores=active_stores,
        total_offers=total_offers,
        active_offers=active_offers,
        recent_stores=store_responses,
        recent_offers=[OfferResponse.from_orm(offer) for offer in recent_offers]
    )
