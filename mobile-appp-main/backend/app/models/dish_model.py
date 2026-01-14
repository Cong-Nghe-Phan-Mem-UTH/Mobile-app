"""
Dish Model - Menu items
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class DishStatus(str, enum.Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"
    OUT_OF_STOCK = "OutOfStock"


class DishModel(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    category = Column(String, nullable=True, index=True)
    status = Column(Enum(DishStatus), default=DishStatus.AVAILABLE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel", back_populates="dishes")
    dish_snapshots = relationship("DishSnapshotModel", back_populates="dish", cascade="all, delete-orphan")
    discounts = relationship("DiscountModel", back_populates="dish", cascade="all, delete-orphan")


class DishSnapshotModel(Base):
    __tablename__ = "dish_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    category = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    dish = relationship("DishModel", back_populates="dish_snapshots")
    order = relationship("OrderModel", back_populates="dish_snapshot", uselist=False)

