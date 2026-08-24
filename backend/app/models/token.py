from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.base import Base

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_number = Column(String(20), nullable=False, index=True) # e.g. 'T-101'
    status = Column(String(30), default="Waiting", nullable=False, index=True) # 'Waiting', 'Preparing', 'Ready', 'Completed', 'Cancelled'
    estimated_wait_minutes = Column(Integer, default=15, nullable=False)
    queue_position = Column(Integer, default=1, nullable=False)
    priority_score = Column(Numeric(5, 2), default=1.0)
    counter_number = Column(Integer, default=1)
    called_at = Column(DateTime(timezone=True), nullable=True)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    order = relationship("Order", back_populates="token")
    user = relationship("User", back_populates="tokens")
