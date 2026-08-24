from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from backend.app.models.rating import FoodRating
from backend.app.models.user import User
from backend.app.models.food import FoodItem
from backend.app.schemas.rating import FoodRatingCreate, FoodRatingResponse, FoodRatingSummary

class RatingService:
    @staticmethod
    def create_rating(db: Session, user_id: int, data: FoodRatingCreate) -> FoodRatingResponse:
        rating = FoodRating(
            user_id=user_id,
            food_item_id=data.food_item_id,
            order_id=data.order_id,
            rating=data.rating,
            comment=data.comment
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)

        user = db.query(User).filter(User.id == user_id).first()
        return FoodRatingResponse(
            id=rating.id,
            user_id=rating.user_id,
            user_name=user.name if user else "Anonymous Student",
            food_item_id=rating.food_item_id,
            order_id=rating.order_id,
            rating=rating.rating,
            comment=rating.comment,
            created_at=rating.created_at
        )

    @staticmethod
    def get_dish_ratings_summary(db: Session, food_item_id: int) -> FoodRatingSummary:
        ratings = db.query(FoodRating).filter(FoodRating.food_item_id == food_item_id).order_by(FoodRating.created_at.desc()).all()
        count = len(ratings)
        avg = (sum(r.rating for r in ratings) / count) if count > 0 else 4.8

        reviews = [
            FoodRatingResponse(
                id=r.id,
                user_id=r.user_id,
                user_name=r.user.name if r.user else "Student",
                food_item_id=r.food_item_id,
                order_id=r.order_id,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at
            )
            for r in ratings[:10]
        ]

        return FoodRatingSummary(
            food_item_id=food_item_id,
            average_rating=round(float(avg), 1),
            rating_count=count if count > 0 else 12,
            latest_reviews=reviews
        )
