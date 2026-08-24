from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_id = Column(String(100), unique=True, nullable=False)
    payment_method = Column(String(50), nullable=False) # 'Card', 'UPI', 'Wallet', 'NetBanking', 'Cash'
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(30), default="Completed", nullable=False) # 'Pending', 'Completed', 'Failed', 'Refunded'
    gateway_response = Column(Text, nullable=True)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="payment")
