from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AchievementResponse(BaseModel):
    id: int
    achievement_key: str
    title: str
    icon: str
    description: str
    unlocked_at: datetime

    class Config:
        from_attributes = True

class UserRewardResponse(BaseModel):
    total_points: int
    tier: str
    current_streak_days: int
    next_tier: str
    points_to_next_tier: int
    achievements: List[AchievementResponse] = []

    class Config:
        from_attributes = True

class LeaderboardUser(BaseModel):
    rank: int
    user_name: str
    total_points: int
    tier: str
    streak_days: int
    badges_count: int

class LeaderboardResponse(BaseModel):
    top_users: List[LeaderboardUser]
    user_rank: Optional[int] = None
