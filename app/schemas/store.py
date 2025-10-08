from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class StoreBase(BaseModel):
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

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
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
    is_active: Optional[bool] = None

class StoreResponse(StoreBase):
    id: str
    owner_id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StoreListResponse(BaseModel):
    stores: List[StoreResponse]
    total: int
    page: int
    limit: int
