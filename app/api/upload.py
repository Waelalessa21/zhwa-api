from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import User
from app.schemas import FileUploadResponse
from app.utils.helpers import save_uploaded_file
import os

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/image", response_model=FileUploadResponse)
def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        filename = save_uploaded_file(file)
        file_path = os.path.join("uploads", filename)
        file_size = os.path.getsize(file_path)
        
        return FileUploadResponse(
            filename=filename,
            url=f"/static/{filename}",
            size=file_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
