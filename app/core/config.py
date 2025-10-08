from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str = "sqlite:///./zhwaweb.db"
    secret_key: str = "PRODUCTINON_SECRET_KEY"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    upload_dir: str = "uploads"
    max_file_size: int = 5242880
    allowed_image_types: List[str] = ["jpg", "jpeg", "png", "gif"]
    
    class Config:
        env_file = ".env"

settings = Settings()
