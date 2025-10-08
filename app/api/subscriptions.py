from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User, Subscription, Store
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, SubscriptionListResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("/", response_model=SubscriptionListResponse)
def get_subscriptions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Subscription)
    
    if current_user.type == "store":
        query = query.filter(Subscription.user_id == current_user.id)
    
    if status:
        query = query.filter(Subscription.status == status)
    
    total = query.count()
    subscriptions = query.offset((page - 1) * limit).limit(limit).all()
    
    subscription_responses = []
    for subscription in subscriptions:
        subscription_dict = subscription.__dict__.copy()
        subscription_dict["products"] = subscription.products.split(",") if subscription.products else []
        if subscription_dict.get("image"):
            subscription_dict["image"] = f"/static/{subscription_dict['image']}"
        subscription_responses.append(SubscriptionResponse(**subscription_dict))
    
    return SubscriptionListResponse(
        subscriptions=subscription_responses,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/check/{email}", response_model=SubscriptionResponse)
def check_subscription_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(Subscription.email == email).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found with this email")
    
    subscription_dict = subscription.__dict__.copy()
    subscription_dict["products"] = subscription.products.split(",") if subscription.products else []
    if subscription_dict.get("image"):
        subscription_dict["image"] = f"/static/{subscription_dict['image']}"
    return SubscriptionResponse(**subscription_dict)

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if current_user.type == "store" and subscription.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    subscription_dict = subscription.__dict__.copy()
    subscription_dict["products"] = subscription.products.split(",") if subscription.products else []
    if subscription_dict.get("image"):
        subscription_dict["image"] = f"/static/{subscription_dict['image']}"
    return SubscriptionResponse(**subscription_dict)

@router.post("/", response_model=SubscriptionResponse)
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    subscription_data = subscription.dict()
    products_str = ",".join(subscription_data.pop("products", []))
    
    db_subscription = Subscription(
        **subscription_data,
        products=products_str,
        user_id=None,
        status="pending"
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    subscription_dict = db_subscription.__dict__.copy()
    subscription_dict["products"] = db_subscription.products.split(",") if db_subscription.products else []
    if subscription_dict.get("image"):
        subscription_dict["image"] = f"/static/{subscription_dict['image']}"
    return SubscriptionResponse(**subscription_dict)

@router.put("/update-by-email/{email}", response_model=SubscriptionResponse)
def update_subscription_by_email(
    email: str,
    subscription_update: SubscriptionUpdate,
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(Subscription.email == email).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found with this email")
    
    if subscription.status == "approved":
        raise HTTPException(status_code=400, detail="Cannot update approved subscription")
    
    update_data = subscription_update.dict(exclude_unset=True)
    if "products" in update_data:
        update_data["products"] = ",".join(update_data["products"])
    
    for field, value in update_data.items():
        setattr(subscription, field, value)
    
    db.commit()
    db.refresh(subscription)
    
    subscription_dict = subscription.__dict__.copy()
    subscription_dict["products"] = subscription.products.split(",") if subscription.products else []
    if subscription_dict.get("image"):
        subscription_dict["image"] = f"/static/{subscription_dict['image']}"
    return SubscriptionResponse(**subscription_dict)

@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: str,
    subscription_update: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if current_user.type == "store" and subscription.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if subscription.status == "approved":
        raise HTTPException(status_code=400, detail="Cannot update approved subscription")
    
    update_data = subscription_update.dict(exclude_unset=True)
    if "products" in update_data:
        update_data["products"] = ",".join(update_data["products"])
    
    for field, value in update_data.items():
        setattr(subscription, field, value)
    
    db.commit()
    db.refresh(subscription)
    
    subscription_dict = subscription.__dict__.copy()
    subscription_dict["products"] = subscription.products.split(",") if subscription.products else []
    if subscription_dict.get("image"):
        subscription_dict["image"] = f"/static/{subscription_dict['image']}"
    return SubscriptionResponse(**subscription_dict)

@router.put("/{subscription_id}/approve", response_model=SubscriptionResponse)
def approve_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Only admins can approve subscriptions")
    
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if subscription.status != "pending":
        raise HTTPException(status_code=400, detail="Subscription is not pending")
    
    subscription.status = "approved"
    db.commit()
    db.refresh(subscription)
    
    subscription_dict = subscription.__dict__.copy()
    subscription_dict["products"] = subscription.products.split(",") if subscription.products else []
    if subscription_dict.get("image"):
        subscription_dict["image"] = f"/static/{subscription_dict['image']}"
    return SubscriptionResponse(**subscription_dict)

@router.put("/{subscription_id}/reject", response_model=SubscriptionResponse)
def reject_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.type != "admin":
        raise HTTPException(status_code=403, detail="Only admins can reject subscriptions")
    
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if subscription.status != "pending":
        raise HTTPException(status_code=400, detail="Subscription is not pending")
    
    subscription.status = "rejected"
    db.commit()
    db.refresh(subscription)
    
    subscription_dict = subscription.__dict__.copy()
    subscription_dict["products"] = subscription.products.split(",") if subscription.products else []
    if subscription_dict.get("image"):
        subscription_dict["image"] = f"/static/{subscription_dict['image']}"
    return SubscriptionResponse(**subscription_dict)

@router.delete("/{subscription_id}")
def delete_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if current_user.type == "store" and subscription.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if subscription.status == "approved":
        raise HTTPException(status_code=400, detail="Cannot delete approved subscription")
    
    db.delete(subscription)
    db.commit()
    return {"message": "Subscription deleted successfully"}
