"""
Restaurant (Tenant) schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class RestaurantCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class RestaurantResponse(BaseModel):
    id: int
    name: str
    slug: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    logo: Optional[str] = None
    description: Optional[str] = None
    status: str
    subscription: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

