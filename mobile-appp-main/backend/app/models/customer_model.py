"""
Customer Model - Mobile App users
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class MembershipTier(str, enum.Enum):
    IRON = "Iron"
    SILVER = "Silver"
    GOLD = "Gold"
    DIAMOND = "Diamond"


class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    membership_tier = Column(Enum(MembershipTier), default=MembershipTier.IRON, nullable=False)
    total_spending = Column(Float, default=0.0, nullable=False)  # Tổng chi tiêu
    points = Column(Integer, default=0, nullable=False)  # Điểm tích lũy
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    reviews = relationship("ReviewModel", back_populates="customer", cascade="all, delete-orphan")
    reservations = relationship("ReservationModel", back_populates="customer", cascade="all, delete-orphan")
    customer_history = relationship("CustomerHistoryModel", back_populates="customer", cascade="all, delete-orphan")

