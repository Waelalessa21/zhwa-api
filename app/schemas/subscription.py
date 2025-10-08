from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class SubscriptionBase(BaseModel):
    name: str
    sector: str
    city: str
    location: str
    image: Optional[str] = None
    description: Optional[str] = None
    address: str
    phone: str
    email: str
    products: List[str] = []

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    city: Optional[str] = None
    location: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    products: Optional[List[str]] = None
    status: Optional[str] = None

class SubscriptionResponse(SubscriptionBase):
    id: str
    user_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SubscriptionListResponse(BaseModel):
    subscriptions: List[SubscriptionResponse]
    total: int
    page: int
    limit: int
