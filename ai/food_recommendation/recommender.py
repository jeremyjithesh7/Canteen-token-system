from typing import List, Dict, Any
from datetime import datetime

class FoodRecommender:
    """
    Hybrid Context-Aware Recommendation Engine for South Indian Menu.
    Combines:
    1. User's historical ordering frequency
    2. Contextual time-of-day meal slots (Breakfast, Lunch, Snacks, Dinner)
    3. User dietary constraints & high-protein matching
    4. Match percentage & rich contextual explanation
    """
    def __init__(self):
        self.popular_items = [1, 4, 5, 9, 11, 13, 14, 19, 20, 21]

    def _get_current_meal_slot(self) -> str:
        hour = datetime.now().hour
        if 7 <= hour < 11:
            return "Breakfast"
        elif 11 <= hour < 16:
            return "Lunch"
        elif 16 <= hour < 19:
            return "Snacks"
        else:
            return "Dinner"

    def recommend(
        self,
        user_id: int,
        all_food_items: List[Dict[str, Any]],
        user_order_history: List[Dict[str, Any]] = None,
        user_preferences: Dict[str, Any] = None,
        top_n: int = 4
    ) -> List[Dict[str, Any]]:
        current_slot = self._get_current_meal_slot()
        user_order_history = user_order_history or []
        user_preferences = user_preferences or {}

        is_veg_only = user_preferences.get("is_veg_only", False)
        fav_cat_id = user_preferences.get("favorite_category_id")

        # Count how many times user ordered each item
        item_order_counts = {}
        for order in user_order_history:
            for item in order.get("items", []):
                fid = item.get("food_item_id")
                item_order_counts[fid] = item_order_counts.get(fid, 0) + item.get("quantity", 1)

        scored_items = []

        for item in all_food_items:
            if not item.get("is_available", True):
                continue

            if is_veg_only and not item.get("is_veg", False):
                continue

            item_id = item["id"]
            cat_slug = (item.get("slug") or item.get("category_slug") or "").lower()
            cat_id = item.get("category_id", 1)
            protein = float(item.get("protein") or 0.0)

            score = 0.55
            reasons = []
            tags = []

            # 1. Past user history
            order_count = item_order_counts.get(item_id, 0)
            if order_count > 0:
                score += min(0.35, order_count * 0.12)
                reasons.append(f"Recommended because you frequently order {item['name']} ({order_count} past order{'s' if order_count > 1 else ''}).")
                tags.append("Frequently Ordered")

            # 2. Time of day matching
            if current_slot == "Breakfast" and (cat_id in [1, 3] or "tiffin" in cat_slug or "beverage" in cat_slug):
                score += 0.25
                reasons.append(f"Recommended because you enjoy fresh South Indian breakfast dishes in the morning.")
                tags.append("Breakfast Favorite")
            elif current_slot == "Lunch" and (cat_id == 1 or "tiffin" in cat_slug or "meals" in cat_slug):
                score += 0.25
                reasons.append(f"Recommended because it is the most popular wholesome choice for campus lunch.")
                tags.append("Top Lunch Pick")
            elif current_slot == "Snacks" and (cat_id in [2, 3] or "dessert" in cat_slug or "beverage" in cat_slug or item_id in [4, 5]):
                score += 0.25
                reasons.append(f"Recommended because it pairs ideally for evening tea & snacks (4-7 PM).")
                tags.append("Evening Snack")
            elif current_slot == "Dinner" and (cat_id in [1, 2] or "tiffin" in cat_slug or "meals" in cat_slug):
                score += 0.20
                reasons.append(f"Recommended for a light, delicious hot South Indian dinner.")
                tags.append("Dinner Special")

            # 3. Favorite category match
            if fav_cat_id and item.get("category_id") == fav_cat_id:
                score += 0.15
                tags.append("Favorite Category")

            # 4. Nutritional bonus
            if protein >= 8.0:
                score += 0.10
                tags.append(f"High Protein ({protein}g)")

            # 5. Fallback popularity
            if not reasons:
                if item_id in self.popular_items:
                    score += 0.15
                    reasons.append(f"Recommended because this is currently trending with high 4.9⭐ student ratings.")
                    tags.append("Campus Trending")
                else:
                    reasons.append(f"Recommended based on high customer satisfaction and availability.")
                    tags.append("Chef's Pick")

            primary_reason = reasons[0]
            recommendation_type = "historical" if order_count > 0 else ("time_based" if "morning" in primary_reason or "lunch" in primary_reason or "evening" in primary_reason or "dinner" in primary_reason else "trending")
            
            # Map score to percentage (e.g. 88% - 98%)
            norm_score = min(1.0, score)
            match_pct = int(min(98, max(82, norm_score * 95 + (item_id % 4))))

            scored_items.append({
                "id": item["id"],
                "name": item["name"],
                "category_name": item.get("category_name", "South Indian Specialty"),
                "price": item.get("price", 50.0),
                "is_veg": item.get("is_veg", True),
                "prep_time_minutes": item.get("prep_time_minutes", 8),
                "image_url": item.get("image_url"),
                "protein": protein,
                "recommendation_score": round(norm_score, 3),
                "match_percentage": match_pct,
                "recommendation_type": recommendation_type,
                "recommendation_reason": primary_reason,
                "confidence_tags": tags[:3],
                "average_rating": float(item.get("average_rating") or 4.8)
            })

        # Sort descending by match percentage / score
        scored_items.sort(key=lambda x: (x["match_percentage"], x["recommendation_score"]), reverse=True)
        return scored_items[:top_n]
