from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class OfferBase(BaseModel):
    title: str
    description: Optional[str] = None
    discount_percentage: int
    image: Optional[str] = None
    valid_until: datetime
    store_id: str

class OfferCreate(OfferBase):
    pass

class OfferUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    discount_percentage: Optional[int] = None
    image: Optional[str] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None

class OfferResponse(OfferBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    store_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class OfferListResponse(BaseModel):
    offers: List[OfferResponse]
    total: int
    page: int
    limit: int
