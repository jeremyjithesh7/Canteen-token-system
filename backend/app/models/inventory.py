from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_stock = Column(Integer, default=0, nullable=False)
    minimum_stock_alert = Column(Integer, default=10, nullable=False)
    unit = Column(String(30), default="portions")
    last_restocked_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    food_item = relationship("FoodItem", back_populates="inventory")

class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    change_amount = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False) # 'order_placed', 'restocked', 'adjustment', 'wastage'
    reference_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
