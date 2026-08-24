from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database.session import get_db
from backend.app.schemas.rating import FoodRatingCreate, FoodRatingResponse, FoodRatingSummary
from backend.app.services.rating_service import RatingService
from backend.app.authentication.deps import get_current_active_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/ratings", tags=["Food Ratings & Reviews"])

@router.post("/", response_model=FoodRatingResponse, status_code=status.HTTP_201_CREATED)
def submit_food_rating(
    data: FoodRatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit 1-5 star rating and comment for a food dish."""
    return RatingService.create_rating(db=db, user_id=current_user.id, data=data)

@router.get("/dish/{food_item_id}", response_model=FoodRatingSummary)
def get_dish_ratings(
    food_item_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve average rating and customer reviews for a specific dish."""
    return RatingService.get_dish_ratings_summary(db=db, food_item_id=food_item_id)
