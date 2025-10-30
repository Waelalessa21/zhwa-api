from typing import List
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Accept both uppercase envs (e.g. DATABASE_URL) and field-name envs
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="sqlite:///./zhwaweb.db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )
    secret_key: str = Field(
        default="PRODUCTINON_SECRET_KEY",
        validation_alias=AliasChoices("SECRET_KEY", "secret_key"),
    )
    algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices("ALGORITHM", "algorithm"),
    )
    access_token_expire_minutes: int = Field(
        default=1440,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "access_token_expire_minutes"),
    )
    upload_dir: str = Field(
        default="uploads",
        validation_alias=AliasChoices("UPLOAD_DIR", "upload_dir"),
    )
    max_file_size: int = Field(
        default=5242880,
        validation_alias=AliasChoices("MAX_FILE_SIZE", "max_file_size"),
    )
    allowed_image_types: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif"],
        validation_alias=AliasChoices("ALLOWED_IMAGE_TYPES", "allowed_image_types"),
    )

    # Optional: allow phone-based admin login
    allow_phone_admin_login: bool = Field(
        default=False,
        validation_alias=AliasChoices("ALLOW_PHONE_ADMIN_LOGIN", "allow_phone_admin_login"),
    )
    admin_username: str = Field(
        default="admin",
        validation_alias=AliasChoices("ADMIN_USERNAME", "admin_username"),
    )
    admin_password: str = Field(
        default="admin",
        validation_alias=AliasChoices("ADMIN_PASSWORD", "admin_password"),
    )

settings = Settings()
