from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

class DemandPredictionItem(BaseModel):
    food_item_id: int
    name: str
    category: str
    predicted_demand: int
    recommended_prep_quantity: int
    safety_buffer: int
    lower_bound: int
    upper_bound: int
    confidence_score: float
    meal_slot: str
    target_date: str
    has_admin_override: bool = False
    override_quantity: Optional[int] = None

class DemandForecastRequest(BaseModel):
    target_date: Optional[date] = None
    meal_slot: Optional[str] = "Lunch" # 'Breakfast', 'Lunch', 'Snacks', 'Dinner'

class DemandForecastResponse(BaseModel):
    forecast_date: str
    meal_slot: str
    total_predicted_items: int
    total_prep_units: int
    items: List[DemandPredictionItem]

class PredictionOverrideCreate(BaseModel):
    food_item_id: int
    prediction_date: date
    meal_slot: str
    override_quantity: int
    reason: Optional[str] = "Manual kitchen adjustment"

class PredictionOverrideResponse(BaseModel):
    id: int
    food_item_id: int
    food_item_name: Optional[str] = None
    prediction_date: date
    meal_slot: str
    original_predicted_quantity: int
    override_quantity: int
    admin_user_id: int
    admin_name: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DemandVsActualPoint(BaseModel):
    date: str
    food_item_id: int
    food_item_name: str
    predicted_demand: int
    actual_demand: int
    variance: int
    accuracy_percentage: float

class DemandVsActualResponse(BaseModel):
    period_days: int
    overall_accuracy: float
    data: List[DemandVsActualPoint]

class FoodRecommendationItem(BaseModel):
    id: int
    name: str
    category_name: str
    price: Decimal
    is_veg: bool
    prep_time_minutes: int
    image_url: Optional[str] = None
    recommendation_score: float
    match_percentage: int = 90
    recommendation_type: str
    recommendation_reason: str
    confidence_tags: List[str] = []
    average_rating: Optional[float] = 4.8
    protein: Optional[Decimal] = Decimal("0.0")

class QueueStatusResponse(BaseModel):
    timestamp: datetime
    total_active_orders: int
    waiting_count: int
    preparing_count: int
    estimated_average_wait_minutes: int
    crowd_level: str
    active_counters: int
    counter_breakdown: Dict[str, Any]
    confidence_score: float
    upcoming_busy_periods: List[Dict[str, Any]]

class CrowdTimelinePoint(BaseModel):
    time_offset: str # 'NOW', '+30m', '+60m', '+120m'
    time_label: str # '12:30 PM'
    crowd_level: str # 'LOW', 'MODERATE', 'HIGH', 'PEAK'
    crowd_color: str # 'green', 'yellow', 'orange', 'red'
    estimated_wait_minutes: int
    expected_order_volume: int

class CrowdForecastResponse(BaseModel):
    current_crowd: str
    current_wait_minutes: int
    forecast_30m: str
    forecast_60m: str
    forecast_120m: str
    expected_peak_time: str
    expected_peak_level: str
    recommendation: str
    timeline: List[CrowdTimelinePoint]

class InventoryIntelligenceItem(BaseModel):
    food_item_id: int
    name: str
    category: str
    current_stock: int
    predicted_demand: int
    recommended_preparation: int
    status: str # 'HIGH DEMAND', 'MODERATE', 'ADEQUATE', 'SURPLUS'
    status_color: str # 'red', 'orange', 'green', 'blue'
    has_override: bool = False
    override_quantity: Optional[int] = None
    override_reason: Optional[str] = None

class InventoryIntelligenceResponse(BaseModel):
    generated_at: str
    meal_slot: str
    total_items_analyzed: int
    total_prep_recommended: int
    high_demand_count: int
    items: List[InventoryIntelligenceItem]
