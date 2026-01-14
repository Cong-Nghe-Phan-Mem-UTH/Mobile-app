"""
Refresh Token Model
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.databases.base import Base


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    account = relationship("AccountModel", back_populates="refresh_tokens")

