"""
Order Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class OrderStatus(str, enum.Enum):
    PENDING = "Pending"
    PREPARING = "Preparing"
    READY = "Ready"
    SERVED = "Served"
    CANCELLED = "Cancelled"
    PAID = "Paid"


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="SET NULL"), nullable=True, index=True)
    table_number = Column(Integer, ForeignKey("tables.number", ondelete="SET NULL"), nullable=True, index=True)
    dish_snapshot_id = Column(Integer, ForeignKey("dish_snapshots.id", ondelete="CASCADE"), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)  # Guest notes for the dish
    order_handler_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel", back_populates="orders")
    branch = relationship("BranchModel", back_populates="orders")
    guest = relationship("GuestModel", back_populates="orders")
    table = relationship("TableModel", back_populates="orders", foreign_keys="[OrderModel.table_number]")
    dish_snapshot = relationship("DishSnapshotModel", back_populates="order", uselist=False)
    order_handler = relationship("AccountModel", foreign_keys="[OrderModel.order_handler_id]")

