from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class TokenStatusUpdate(BaseModel):
    status: str # 'Waiting', 'Preparing', 'Ready', 'Completed', 'Cancelled'
    counter_number: Optional[int] = None

class TokenResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    token_number: str
    status: str
    estimated_wait_minutes: int
    queue_position: int
    priority_score: Optional[Decimal] = None
    counter_number: int
    order_number: Optional[str] = None
    user_name: Optional[str] = None
    items_summary: Optional[str] = None
    total_amount: Optional[Decimal] = None
    called_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LiveQueueStatus(BaseModel):
    active_tokens_count: int
    waiting_count: int
    preparing_count: int
    ready_count: int
    estimated_average_wait: int
    crowd_level: str
    tokens: List[TokenResponse] = []
