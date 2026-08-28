from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

class FoodRatingCreate(BaseModel):
    food_item_id: int
    order_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=500, description="Customer review comment")

class FoodRatingResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    food_item_id: int
    order_id: Optional[int] = None
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FoodRatingSummary(BaseModel):
    food_item_id: int
    average_rating: Optional[float] = None
    rating_count: int = 0
    star_counts: Dict[int, int] = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    latest_reviews: List[FoodRatingResponse] = []
