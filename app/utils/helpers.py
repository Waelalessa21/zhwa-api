import os
import shutil
from typing import List
from fastapi import HTTPException, UploadFile
from app.core.config import settings

def validate_file_type(file: UploadFile) -> bool:
    if not file.filename:
        return False
    file_extension = file.filename.split('.')[-1].lower()
    return file_extension in settings.allowed_image_types

def validate_file_size(file: UploadFile) -> bool:
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    return file_size <= settings.max_file_size

def save_uploaded_file(file: UploadFile, upload_dir: str = None) -> str:
    if upload_dir is None:
        upload_dir = settings.upload_dir
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    if not validate_file_type(file):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    if not validate_file_size(file):
        raise HTTPException(status_code=400, detail="File too large")
    
    file_extension = file.filename.split('.')[-1].lower()
    filename = f"{os.urandom(16).hex()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return filename

def delete_file(filename: str, upload_dir: str = None) -> bool:
    if upload_dir is None:
        upload_dir = settings.upload_dir
    
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
