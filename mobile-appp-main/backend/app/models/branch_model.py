"""
Branch Model - Multi-branch support
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class BranchStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class BranchModel(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    status = Column(Enum(BranchStatus), default=BranchStatus.ACTIVE, nullable=False)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel", back_populates="branches")
    tables = relationship("TableModel", back_populates="branch", cascade="all, delete-orphan")
    orders = relationship("OrderModel", back_populates="branch", cascade="all, delete-orphan")

