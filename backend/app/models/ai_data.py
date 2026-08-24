from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.base import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    favorite_category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    is_veg_only = Column(Boolean, default=False)
    spice_level = Column(String(20), default="Medium")
    dietary_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    score = Column(Numeric(5, 3), nullable=False)
    recommendation_type = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id = Column(Integer, primary_key=True, index=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    prediction_date = Column(Date, nullable=False)
    meal_slot = Column(String(30), nullable=False)
    predicted_quantity = Column(Integer, nullable=False)
    lower_bound = Column(Integer, nullable=False)
    upper_bound = Column(Integer, nullable=False)
    confidence_score = Column(Numeric(4, 3), nullable=False)
    actual_quantity = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictionOverride(Base):
    __tablename__ = "prediction_overrides"

    id = Column(Integer, primary_key=True, index=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    prediction_date = Column(Date, nullable=False)
    meal_slot = Column(String(30), nullable=False) # 'Breakfast', 'Lunch', 'Snacks', 'Dinner'
    original_predicted_quantity = Column(Integer, nullable=False)
    override_quantity = Column(Integer, nullable=False)
    admin_user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    food_item = relationship("FoodItem")
    admin_user = relationship("User")


class QueuePrediction(Base):
    __tablename__ = "queue_predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    queue_depth = Column(Integer, nullable=False)
    estimated_wait_minutes = Column(Integer, nullable=False)
    crowd_level = Column(String(20), nullable=False)
    confidence = Column(Numeric(4, 3), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
