from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from fastapi import HTTPException, status

from backend.app.models.rating import FoodRating
from backend.app.models.user import User
from backend.app.models.food import FoodItem
from backend.app.models.order import Order, OrderItem
from backend.app.schemas.rating import FoodRatingCreate, FoodRatingResponse, FoodRatingSummary

class RatingService:
    @staticmethod
    def create_rating(db: Session, user_id: int, data: FoodRatingCreate) -> FoodRatingResponse:
        # 1. Verify food item exists
        food = db.query(FoodItem).filter(FoodItem.id == data.food_item_id).first()
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food dish not found.")

        # 2. Verify student has actually purchased this item in a valid order
        purchased = db.query(OrderItem).join(Order).filter(
            Order.user_id == user_id,
            OrderItem.food_item_id == data.food_item_id,
            Order.status.in_(["Confirmed", "Preparing", "Ready", "Completed"])
        ).first()

        if not purchased:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You can only rate dishes you have ordered. Please order {food.name} first!"
            )

        # 3. Check for duplicate review (allow update to avoid review spam)
        existing_query = db.query(FoodRating).filter(
            FoodRating.user_id == user_id,
            FoodRating.food_item_id == data.food_item_id
        )
        if data.order_id:
            existing_query = existing_query.filter(FoodRating.order_id == data.order_id)
        
        rating = existing_query.first()

        if rating:
            rating.rating = data.rating
            rating.comment = data.comment
            if data.order_id:
                rating.order_id = data.order_id
            db.commit()
            db.refresh(rating)
        else:
            rating = FoodRating(
                user_id=user_id,
                food_item_id=data.food_item_id,
                order_id=data.order_id or (purchased.order_id if purchased else None),
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
        
        star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in ratings:
            if 1 <= r.rating <= 5:
                star_counts[r.rating] += 1

        avg = (sum(r.rating for r in ratings) / count) if count > 0 else None

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
            for r in ratings[:20]
        ]

        return FoodRatingSummary(
            food_item_id=food_item_id,
            average_rating=round(float(avg), 1) if avg is not None else None,
            rating_count=count,
            star_counts=star_counts,
            latest_reviews=reviews
        )
