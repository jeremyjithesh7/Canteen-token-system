from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from .food import FoodItemResponse

class OrderItemCreate(BaseModel):
    food_item_id: int
    quantity: int = Field(1, gt=0)
    special_instructions: Optional[str] = None

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    payment_method: str = "UPI" # 'Card', 'UPI', 'Wallet', 'NetBanking', 'Cash'
    notes: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    is_preorder: bool = False

class OrderItemResponse(BaseModel):
    id: int
    food_item_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    special_instructions: Optional[str] = None
    food_item: Optional[FoodItemResponse] = None

    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: str # 'Confirmed', 'Preparing', 'Ready', 'Completed', 'Cancelled'

class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_number: str
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    status: str
    notes: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    is_preorder: bool = False
    items: List[OrderItemResponse] = []
    token_number: Optional[str] = None
    token_status: Optional[str] = None
    estimated_wait_minutes: Optional[int] = None
    queue_position: Optional[int] = None
    counter_number: Optional[int] = None
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
