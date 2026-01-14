"""
Guest Model - QR code users
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.databases.base import Base


class GuestModel(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    table_number = Column(Integer, ForeignKey("tables.number", ondelete="SET NULL"), nullable=True, index=True)
    refresh_token = Column(String, nullable=True)
    refresh_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel", back_populates="guests")
    table = relationship("TableModel", back_populates="guests", foreign_keys=[table_number])
    orders = relationship("OrderModel", back_populates="guest", cascade="all, delete-orphan")
    sockets = relationship("SocketModel", back_populates="guest", cascade="all, delete-orphan")

