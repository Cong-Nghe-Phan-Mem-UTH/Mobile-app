"""
Tenant Model - Multi-tenant support
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class TenantStatus(str, enum.Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    INACTIVE = "Inactive"


class SubscriptionType(str, enum.Enum):
    FREE = "Free"
    BASIC = "Basic"
    PREMIUM = "Premium"


class TenantModel(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(Enum(TenantStatus), default=TenantStatus.ACTIVE, nullable=False)
    subscription = Column(Enum(SubscriptionType), default=SubscriptionType.FREE, nullable=False)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    accounts = relationship("AccountModel", back_populates="tenant")
    dishes = relationship("DishModel", back_populates="tenant")
    tables = relationship("TableModel", back_populates="tenant")
    orders = relationship("OrderModel", back_populates="tenant")
    guests = relationship("GuestModel", back_populates="tenant")
    branches = relationship("BranchModel", back_populates="tenant")
    discounts = relationship("DiscountModel", back_populates="tenant")
    reviews = relationship("ReviewModel", back_populates="tenant")
    reservations = relationship("ReservationModel", back_populates="tenant")
    customer_history = relationship("CustomerHistoryModel", back_populates="tenant")

