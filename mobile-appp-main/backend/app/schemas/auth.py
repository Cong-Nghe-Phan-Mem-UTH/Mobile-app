"""
Auth schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    avatar: Optional[str] = None
    role: str
    tenant_id: Optional[int] = None

    class Config:
        from_attributes = True

