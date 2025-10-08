from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    type = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    stores = relationship("Store", back_populates="owner")
    subscriptions = relationship("Subscription", back_populates="user")

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    sector = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    image = Column(String(255))
    description = Column(Text)
    address = Column(Text, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    products = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="stores")
    offers = relationship("Offer", back_populates="store")

class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    discount_percentage = Column(Integer, nullable=False)
    image = Column(String(255))
    valid_until = Column(DateTime(timezone=True), nullable=False)
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    store = relationship("Store", back_populates="offers")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    sector = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    image = Column(String(255))
    description = Column(Text)
    address = Column(Text, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    products = Column(Text)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="subscriptions")
