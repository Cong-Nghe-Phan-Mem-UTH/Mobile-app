"""
Account Model - Users (Admin, Owner, Employee, etc.)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class AccountRole(str, enum.Enum):
    ADMIN = "Admin"
    OWNER = "Owner"
    MANAGER = "Manager"
    EMPLOYEE = "Employee"
    CASHIER = "Cashier"
    KITCHEN = "Kitchen"


class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    role = Column(Enum(AccountRole), default=AccountRole.EMPLOYEE, nullable=False)
    permissions = Column(JSON, nullable=True)
    owner_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel", back_populates="accounts")
    owner = relationship("AccountModel", remote_side=[id], backref="employees")
    orders = relationship("OrderModel", foreign_keys="[OrderModel.order_handler_id]")
    refresh_tokens = relationship("RefreshTokenModel", back_populates="account")
    sockets = relationship("SocketModel", back_populates="account")

