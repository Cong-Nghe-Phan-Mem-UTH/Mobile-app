"""
Table Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class TableStatus(str, enum.Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    RESERVED = "Reserved"
    CLEANING = "Cleaning"


class TableModel(Base):
    __tablename__ = "tables"

    number = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True)
    capacity = Column(Integer, nullable=False)
    status = Column(Enum(TableStatus), default=TableStatus.AVAILABLE, nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)  # QR code token
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint: table number per tenant
    __table_args__ = (
        UniqueConstraint('number', 'tenant_id', name='uq_table_tenant'),
    )

    # Relationships
    tenant = relationship("TenantModel", back_populates="tables")
    branch = relationship("BranchModel", back_populates="tables")
    orders = relationship("OrderModel", back_populates="table", foreign_keys="[OrderModel.table_number]")
    guests = relationship("GuestModel", back_populates="table", foreign_keys="[GuestModel.table_number]")

