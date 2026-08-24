from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CounterBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    station_type: str
    is_active: bool = True
    display_order: int = 0

class CounterCreate(CounterBase):
    pass

class CounterUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    station_type: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

class CounterResponse(CounterBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
