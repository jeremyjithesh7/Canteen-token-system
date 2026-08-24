from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: Optional[str] = "announcement"
    reference_id: Optional[str] = None

class NotificationBroadcast(BaseModel):
    title: str
    message: str
    type: Optional[str] = "announcement"

BroadcastNotificationCreate = NotificationBroadcast

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    reference_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
