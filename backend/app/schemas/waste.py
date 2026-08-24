from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal

class FoodWasteItem(BaseModel):
    food_item_id: int
    name: str
    category: str
    prepared_quantity: int
    sold_quantity: int
    leftover_quantity: int
    waste_quantity: int
    waste_percentage: float
    waste_cost_inr: float
    waste_reason: str

class WasteDayTrend(BaseModel):
    date: str
    day_name: str
    total_prepared: int
    total_sold: int
    total_wasted: int
    waste_percentage: float
    loss_inr: float

class FoodWasteAnalyticsResponse(BaseModel):
    total_prepared_portions: int
    total_sold_portions: int
    total_waste_portions: int
    overall_waste_percentage: float
    total_financial_loss_inr: float
    most_wasted_dishes: List[FoodWasteItem]
    weekly_trend: List[WasteDayTrend]
    ai_waste_reduction_suggestions: List[str]
