"""
Review Model - Customer reviews
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.databases.base import Base


class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(String, nullable=True)
    dish_ratings = Column(JSON, nullable=True)  # Ratings for specific dishes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("TenantModel", back_populates="reviews")
    customer = relationship("CustomerModel", back_populates="reviews")

