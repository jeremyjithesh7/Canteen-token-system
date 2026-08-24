from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class CartItemPayload(BaseModel):
    food_item_id: int
    quantity: int = Field(1, ge=1, le=20)
    special_notes: Optional[str] = Field(None, max_length=200)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=0, le=20)
    special_notes: Optional[str] = Field(None, max_length=200)

class CartItemDetail(BaseModel):
    id: int
    food_item_id: int
    name: str
    price: Decimal
    quantity: int
    subtotal: Decimal
    image_url: Optional[str] = None
    counter_id: Optional[int] = 1
    category_name: Optional[str] = None
    is_veg: bool = True
    prep_time_minutes: int = 10
    is_available: bool = True
    current_stock: int = 50
    special_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CartSummaryResponse(BaseModel):
    items: List[CartItemDetail]
    total_items_count: int
    subtotal: Decimal
    gst_tax_amount: Decimal # 5% canteen GST
    grand_total: Decimal

class CartSyncPayload(BaseModel):
    items: List[CartItemPayload]
