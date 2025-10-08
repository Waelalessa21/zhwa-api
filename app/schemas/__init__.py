from pydantic import BaseModel
from typing import List, Optional
from app.schemas.store import StoreResponse
from app.schemas.offer import OfferResponse

class DashboardStats(BaseModel):
    total_stores: int
    active_stores: int
    total_offers: int
    active_offers: int
    recent_stores: List[StoreResponse]
    recent_offers: List[OfferResponse]

class FileUploadResponse(BaseModel):
    filename: str
    url: str
    size: int

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[str] = None
