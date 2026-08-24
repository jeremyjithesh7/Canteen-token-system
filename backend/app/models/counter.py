from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.base import Base

class Counter(Base):
    __tablename__ = "counters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False, index=True) # 'C1', 'C2', 'C3'
    description = Column(Text, nullable=True)
    station_type = Column(String(100), nullable=False) # 'South Indian & Breakfast', 'Fast Food & Snacks', 'Beverages & Coolers'
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    food_items = relationship("FoodItem", back_populates="counter")
