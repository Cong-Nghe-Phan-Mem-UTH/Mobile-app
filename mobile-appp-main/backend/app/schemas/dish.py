"""
Dish schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DishCreate(BaseModel):
    name: str
    price: int
    description: str
    image: str
    category: Optional[str] = None
    status: Optional[str] = "Available"


class DishUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class DishResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    price: int
    description: str
    image: str
    category: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DishListResponse(BaseModel):
    items: list[DishResponse]
    total: int
    page: int
    limit: int

