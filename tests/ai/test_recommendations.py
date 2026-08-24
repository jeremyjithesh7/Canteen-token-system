import pytest
from ai.food_recommendation.recommender import FoodRecommender

def test_recommendation_filtering_and_scoring():
    recommender = FoodRecommender()
    catalog = [
        {"id": 1, "name": "Masala Dosa", "category_id": 1, "category_slug": "breakfast", "is_veg": True, "is_available": True, "protein": 8.0},
        {"id": 6, "name": "Chicken Biryani", "category_id": 2, "category_slug": "meals", "is_veg": False, "is_available": True, "protein": 32.0},
        {"id": 14, "name": "Kulhad Chai", "category_id": 4, "category_slug": "beverages", "is_veg": True, "is_available": True, "protein": 2.0},
        {"id": 99, "name": "Sold Out Item", "category_id": 3, "category_slug": "snacks", "is_veg": True, "is_available": False, "protein": 5.0}
    ]

    # Test 1: Vegetarian user preference excludes non-veg
    veg_prefs = {"is_veg_only": True}
    recs_veg = recommender.recommend(user_id=2, all_food_items=catalog, user_preferences=veg_prefs)
    assert all(r["is_veg"] is True for r in recs_veg)
    assert not any(r["name"] == "Chicken Biryani" for r in recs_veg)

    # Test 2: Unavailable items are omitted
    assert not any(r["name"] == "Sold Out Item" for r in recs_veg)

    # Test 3: Recommendations have valid scores and explanation badges
    for r in recs_veg:
        assert 0.0 <= r["recommendation_score"] <= 1.0
        assert len(r["recommendation_reason"]) > 0
