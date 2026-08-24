from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.base import Base

class UserReward(Base):
    __tablename__ = "user_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_points = Column(Integer, default=50, nullable=False)
    tier = Column(String(50), default="Bronze Explorer", nullable=False) # Bronze Explorer, Silver Foodie, Gold Gourmet, Platinum Master
    current_streak_days = Column(Integer, default=1, nullable=False)
    last_order_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="rewards")

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_key = Column(String(50), nullable=False) # 'FIRST_ORDER', 'STREAK_7', 'COFFEE_LOVER', 'FOODIE', 'ORDERS_10'
    title = Column(String(100), nullable=False)
    icon = Column(String(20), default="🏆", nullable=False)
    description = Column(String(255), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="achievements")
