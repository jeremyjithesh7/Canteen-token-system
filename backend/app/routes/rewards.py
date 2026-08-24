from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.database.session import get_db
from backend.app.schemas.rewards import UserRewardResponse, LeaderboardResponse
from backend.app.services.rewards_service import RewardsService
from backend.app.authentication.deps import get_current_active_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/rewards", tags=["Rewards & Gamification"])

@router.get("/me", response_model=UserRewardResponse)
def get_my_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns student's reward points, tier, order streak, and unlocked badges."""
    return RewardsService.get_user_rewards_summary(db=db, user_id=current_user.id)

@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_campus_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Returns top student foodies on campus with ranks and badges."""
    return RewardsService.get_leaderboard(db=db, current_user_id=current_user.id)
