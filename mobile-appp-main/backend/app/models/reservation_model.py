"""
Reservation Model - Table booking
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.infrastructure.databases.base import Base


class ReservationStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class ReservationModel(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    table_number = Column(Integer, nullable=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    time = Column(String, nullable=False)
    guests = Column(Integer, nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel", back_populates="reservations")
    customer = relationship("CustomerModel", back_populates="reservations")

