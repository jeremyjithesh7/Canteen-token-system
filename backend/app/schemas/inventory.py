from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InventoryUpdate(BaseModel):
    current_stock: Optional[int] = Field(None, ge=0)
    add_quantity: Optional[int] = None
    minimum_stock_alert: Optional[int] = Field(None, ge=0)
    reason: Optional[str] = "Manual restock"

class InventoryRestock(BaseModel):
    add_quantity: int = Field(..., ge=1)
    reason: Optional[str] = "Manual restock"

class InventoryResponse(BaseModel):
    id: int
    food_item_id: int
    food_item_name: Optional[str] = None
    category_name: Optional[str] = None
    current_stock: int
    minimum_stock_alert: int
    unit: str
    is_low_stock: bool = False
    last_restocked_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InventoryLogResponse(BaseModel):
    id: int
    food_item_id: int
    change_amount: int
    reason: str
    reference_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
