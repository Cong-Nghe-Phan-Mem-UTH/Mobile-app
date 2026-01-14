"""
Socket Model - For real-time connections
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.databases.base import Base


class SocketModel(Base):
    __tablename__ = "sockets"

    socket_id = Column(String, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, unique=True)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="SET NULL"), nullable=True, unique=True)
    tenant_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    account = relationship("AccountModel", back_populates="sockets")
    guest = relationship("GuestModel", back_populates="sockets")

