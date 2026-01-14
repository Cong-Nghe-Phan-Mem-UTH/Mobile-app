"""
Discount Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class DiscountType(str, enum.Enum):
    PERCENTAGE = "Percentage"
    FIXED_AMOUNT = "FixedAmount"


class DiscountStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    EXPIRED = "Expired"


class DiscountModel(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(DiscountType), nullable=False)
    value = Column(Integer, nullable=False)  # Percentage or amount
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(DiscountStatus), default=DiscountStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel", back_populates="discounts")
    dish = relationship("DishModel", back_populates="discounts")

