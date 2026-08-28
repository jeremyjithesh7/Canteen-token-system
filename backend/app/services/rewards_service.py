from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from backend.app.models.rewards import UserReward, UserAchievement
from backend.app.models.user import User
from backend.app.models.order import Order, OrderItem

TIER_THRESHOLDS = [
    ("Bronze Explorer", 0, 150, "Silver Foodie"),
    ("Silver Foodie", 150, 400, "Gold Gourmet"),
    ("Gold Gourmet", 400, 1000, "Platinum Master"),
    ("Platinum Master", 1000, 999999, "Campus Legend")
]

class RewardsService:
    @staticmethod
    def get_or_create_rewards(db: Session, user_id: int) -> UserReward:
        reward = db.query(UserReward).filter(UserReward.user_id == user_id).first()
        if not reward:
            reward = UserReward(
                user_id=user_id,
                total_points=0,
                tier="Bronze Explorer",
                current_streak_days=0,
                last_order_date=None
            )
            db.add(reward)
            db.commit()
            db.refresh(reward)
        return reward

    @staticmethod
    def get_user_rewards_summary(db: Session, user_id: int) -> Dict[str, Any]:
        reward = RewardsService.get_or_create_rewards(db, user_id)
        achievements = db.query(UserAchievement).filter(UserAchievement.user_id == user_id).order_by(UserAchievement.unlocked_at.desc()).all()

        current_tier = reward.tier
        next_tier = "Silver Foodie"
        points_to_next = 65

        for name, lower, upper, nxt in TIER_THRESHOLDS:
            if lower <= reward.total_points < upper:
                current_tier = name
                next_tier = nxt
                points_to_next = max(0, upper - reward.total_points)
                break

        return {
            "total_points": reward.total_points,
            "tier": current_tier,
            "current_streak_days": reward.current_streak_days,
            "next_tier": next_tier,
            "points_to_next_tier": points_to_next,
            "achievements": achievements
        }

    @staticmethod
    def process_order_rewards(db: Session, user_id: int, order_amount: Decimal) -> Dict[str, Any]:
        reward = RewardsService.get_or_create_rewards(db, user_id)
        
        # 1 Point per ₹10 spent
        earned_points = max(5, int(order_amount / Decimal("10.0")))
        reward.total_points += earned_points

        # Streak calculation
        today = date.today()
        if reward.last_order_date:
            if reward.last_order_date == today - timedelta(days=1):
                reward.current_streak_days += 1
            elif reward.last_order_date < today - timedelta(days=1):
                reward.current_streak_days = 1
        else:
            reward.current_streak_days = 1

        reward.last_order_date = today

        # Tier calculation
        for name, lower, upper, _ in TIER_THRESHOLDS:
            if lower <= reward.total_points < upper:
                reward.tier = name
                break

        reward.updated_at = datetime.utcnow()
        db.commit()

        # Check and unlock achievements
        RewardsService._evaluate_achievements(db, user_id, reward)

        return {
            "earned_points": earned_points,
            "total_points": reward.total_points,
            "tier": reward.tier,
            "streak": reward.current_streak_days
        }

    @staticmethod
    def _evaluate_achievements(db: Session, user_id: int, reward: UserReward):
        existing_keys = {a.achievement_key for a in db.query(UserAchievement.achievement_key).filter(UserAchievement.user_id == user_id).all()}
        
        order_count = db.query(Order).filter(Order.user_id == user_id).count()

        new_badges = []
        if "FIRST_ORDER" not in existing_keys and order_count >= 1:
            new_badges.append(UserAchievement(user_id=user_id, achievement_key="FIRST_ORDER", title="First Order Placed", icon="🏆", description="Placed your first digital canteen order!"))
        
        if "STREAK_7" not in existing_keys and reward.current_streak_days >= 7:
            new_badges.append(UserAchievement(user_id=user_id, achievement_key="STREAK_7", title="7-Day Canteen Streak", icon="🔥", description="Ordered food for 7 consecutive days!"))

        if "ORDERS_10" not in existing_keys and order_count >= 10:
            new_badges.append(UserAchievement(user_id=user_id, achievement_key="ORDERS_10", title="Loyal Diner", icon="⭐", description="Placed over 10 orders in the canteen!"))

        # Check for coffee lover
        coffee_orders = db.query(OrderItem).join(Order).filter(Order.user_id == user_id, OrderItem.food_item_id == 19).count()
        if "COFFEE_LOVER" not in existing_keys and coffee_orders >= 3:
            new_badges.append(UserAchievement(user_id=user_id, achievement_key="COFFEE_LOVER", title="Degree Coffee Fanatic", icon="☕", description="Ordered authentic Degree Filter Coffee 3+ times!"))

        if "FOODIE" not in existing_keys and reward.total_points >= 250:
            new_badges.append(UserAchievement(user_id=user_id, achievement_key="FOODIE", title="Campus Foodie Pro", icon="🍛", description="Earned 250+ reward points exploring the menu!"))

        for b in new_badges:
            db.add(b)
        if new_badges:
            db.commit()

    @staticmethod
    def get_leaderboard(db: Session, current_user_id: int = None) -> Dict[str, Any]:
        # Top 10 users by reward points
        top_rewards = db.query(UserReward, User.name).join(User, UserReward.user_id == User.id).order_by(UserReward.total_points.desc()).limit(10).all()

        leaderboard = []
        user_rank = None

        for idx, (rew, name) in enumerate(top_rewards, start=1):
            badge_cnt = db.query(UserAchievement).filter(UserAchievement.user_id == rew.user_id).count()
            leaderboard.append({
                "rank": idx,
                "user_name": name,
                "total_points": rew.total_points,
                "tier": rew.tier,
                "streak_days": rew.current_streak_days,
                "badges_count": badge_cnt
            })
            if current_user_id and rew.user_id == current_user_id:
                user_rank = idx

        return {
            "top_users": leaderboard,
            "user_rank": user_rank or 1
        }
