"""
Table schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TableCreate(BaseModel):
    number: int
    capacity: int
    branch_id: Optional[int] = None


class TableUpdate(BaseModel):
    capacity: Optional[int] = None
    status: Optional[str] = None


class TableResponse(BaseModel):
    number: int
    tenant_id: int
    branch_id: Optional[int] = None
    capacity: int
    status: str
    token: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

