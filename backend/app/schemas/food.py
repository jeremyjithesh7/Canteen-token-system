from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date, time
from backend.app.schemas.counter import CounterResponse

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    display_order: int = 0
    icon: Optional[str] = "utensils"
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FoodItemBase(BaseModel):
    name: str
    category_id: int
    counter_id: Optional[int] = None
    description: Optional[str] = None
    price: Decimal
    prep_time_minutes: int = 10
    is_veg: bool = True
    is_vegan: bool = False
    is_available: bool = True
    image_url: Optional[str] = None
    calories: Optional[int] = 0
    protein: Optional[Decimal] = Decimal("0.0")
    carbs: Optional[Decimal] = Decimal("0.0")
    fats: Optional[Decimal] = Decimal("0.0")

class FoodItemCreate(FoodItemBase):
    initial_stock: Optional[int] = 50

class FoodItemUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    counter_id: Optional[int] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    prep_time_minutes: Optional[int] = None
    is_veg: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[Decimal] = None
    carbs: Optional[Decimal] = None
    fats: Optional[Decimal] = None

class FoodItemResponse(FoodItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    counter: Optional[CounterResponse] = None
    current_stock: Optional[int] = 0
    average_rating: float = 4.8
    rating_count: int = 12

    model_config = ConfigDict(from_attributes=True)


class MenuItemResponse(BaseModel):
    id: int
    food_item_id: int
    daily_stock_limit: int
    food_item: Optional[FoodItemResponse] = None

    model_config = ConfigDict(from_attributes=True)


class MenuResponse(BaseModel):
    id: int
    menu_date: date
    is_active: bool
    items: List[MenuItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
