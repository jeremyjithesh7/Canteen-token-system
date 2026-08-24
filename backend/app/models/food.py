from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, DateTime, Date, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date, time
from backend.app.database.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    icon = Column(String(50), default="utensils")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    food_items = relationship("FoodItem", back_populates="category")


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    counter_id = Column(Integer, ForeignKey("counters.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    prep_time_minutes = Column(Integer, default=10, nullable=False)
    is_veg = Column(Boolean, default=True)
    is_vegan = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    image_url = Column(Text, nullable=True)
    calories = Column(Integer, default=0)
    protein = Column(Numeric(5, 1), default=0.0)
    carbs = Column(Numeric(5, 1), default=0.0)
    fats = Column(Numeric(5, 1), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="food_items")
    counter = relationship("Counter", back_populates="food_items")
    inventory = relationship("Inventory", back_populates="food_item", uselist=False)
    order_items = relationship("OrderItem", back_populates="food_item")
    menu_items = relationship("MenuItem", back_populates="food_item")
    ratings = relationship("FoodRating", back_populates="food_item", cascade="all, delete-orphan")
    cart_entries = relationship("CartItem", back_populates="food_item", cascade="all, delete-orphan")
    waste_logs = relationship("FoodWasteLog", back_populates="food_item", cascade="all, delete-orphan")


class Menu(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True)
    menu_date = Column(Date, unique=True, default=date.today, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("MenuItem", back_populates="menu", cascade="all, delete-orphan")


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (UniqueConstraint('menu_id', 'food_item_id', name='uq_menu_food_item'),)

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menu.id", ondelete="CASCADE"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    daily_stock_limit = Column(Integer, default=100)
    available_from = Column(Time, default=time(7, 0))
    available_until = Column(Time, default=time(21, 0))
    created_at = Column(DateTime, default=datetime.utcnow)

    menu = relationship("Menu", back_populates="items")
    food_item = relationship("FoodItem", back_populates="menu_items")
