from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.base import Base

class FoodWasteLog(Base):
    __tablename__ = "food_waste_logs"

    id = Column(Integer, primary_key=True, index=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False, index=True)
    meal_slot = Column(String(50), nullable=False) # 'Breakfast', 'Lunch', 'Snacks', 'Dinner'
    prepared_quantity = Column(Integer, nullable=False)
    sold_quantity = Column(Integer, nullable=False)
    leftover_quantity = Column(Integer, nullable=False)
    waste_quantity = Column(Integer, nullable=False)
    waste_percentage = Column(Numeric(5, 2), nullable=False)
    waste_cost_inr = Column(Numeric(10, 2), nullable=False)
    waste_reason = Column(String(255), default="Over-preparation & unsold buffer")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    food_item = relationship("FoodItem", back_populates="waste_logs")
