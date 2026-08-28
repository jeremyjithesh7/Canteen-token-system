from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = 3 # Default Student

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(UserBase):
    id: int
    role_id: int
    is_active: bool
    created_at: datetime
    role: Optional[RoleResponse] = None
    loyalty_tier: Optional[str] = "Bronze"
    loyalty_badge: Optional[str] = "🥉 Bronze Member"
    total_orders_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TokenAuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserResponse


class UserPreferenceUpdate(BaseModel):
    favorite_category_id: Optional[int] = None
    is_veg_only: Optional[bool] = False
    spice_level: Optional[str] = "Medium"
    dietary_notes: Optional[str] = None

class UserPreferenceResponse(UserPreferenceUpdate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
