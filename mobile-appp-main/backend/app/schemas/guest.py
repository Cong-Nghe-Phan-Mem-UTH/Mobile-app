"""
Guest schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GuestLoginRequest(BaseModel):
    name: str
    table_token: str  # QR code token


class GuestResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    table_number: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

