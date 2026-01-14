"""
Order schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderCreate(BaseModel):
    dish_id: int
    quantity: int
    table_number: Optional[int] = None
    notes: Optional[str] = None


class OrdersCreate(BaseModel):
    orders: list[OrderCreate]
    table_number: Optional[int] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    order_handler_id: Optional[int] = None


class OrderResponse(BaseModel):
    id: int
    tenant_id: int
    branch_id: Optional[int] = None
    guest_id: Optional[int] = None
    table_number: Optional[int] = None
    dish_snapshot_id: int
    quantity: int
    notes: Optional[str] = None
    order_handler_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int

