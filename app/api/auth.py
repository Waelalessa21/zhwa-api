from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from app.models import User
from app.schemas.user import UserCreate, UserLogin, PhoneLogin, Token, UserResponse
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.post("/login-phone", response_model=Token)
def login_with_phone(payload: PhoneLogin, db: Session = Depends(get_db)):
    if not settings.allow_phone_admin_login:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Phone login is disabled")

    # Ensure admin user exists
    admin = db.query(User).filter(User.username == settings.admin_username).first()
    if not admin:
        hashed = get_password_hash(settings.admin_password)
        admin = User(username=settings.admin_username, password_hash=hashed, type="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)

    # Authenticate with configured admin credentials
    user = authenticate_user(db, settings.admin_username, settings.admin_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin credentials invalid")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    return {"message": "Successfully logged out"}

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        type=user.type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse.from_orm(db_user)
