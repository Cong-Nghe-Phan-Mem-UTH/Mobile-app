"""
Customer History Model - Lịch sử món ăn và nhà hàng đã ghé
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.databases.base import Base


class CustomerHistoryModel(Base):
    __tablename__ = "customer_history"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    dish_ids = Column(JSON, nullable=True)  # List of dish IDs đã ăn
    total_amount = Column(Float, nullable=False)  # Tổng tiền của lần ghé này
    visit_date = Column(DateTime(timezone=True), nullable=False, index=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    customer = relationship("CustomerModel", back_populates="customer_history")
    tenant = relationship("TenantModel", back_populates="customer_history")
    order = relationship("OrderModel", foreign_keys=[order_id])

