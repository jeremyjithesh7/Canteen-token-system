import pytest
from datetime import date, timedelta
from ai.demand_prediction.model import DemandPredictionModel

def test_single_item_demand_prediction():
    model = DemandPredictionModel()
    result = model.predict_item_demand(
        item_id=1,
        item_name="Masala Dosa",
        category_slug="breakfast",
        target_date=date.today() + timedelta(days=1),
        meal_slot="Breakfast"
    )
    assert result["food_item_id"] == 1
    assert result["predicted_demand"] > 0
    assert result["recommended_prep_quantity"] >= result["predicted_demand"]
    assert result["lower_bound"] <= result["predicted_demand"]
    assert result["upper_bound"] >= result["predicted_demand"]
    assert 0.60 <= result["confidence_score"] <= 1.0

def test_all_menu_demand_prediction():
    model = DemandPredictionModel()
    catalog = [
        {"id": 1, "name": "Masala Dosa", "category_slug": "breakfast"},
        {"id": 5, "name": "North Indian Thali", "category_slug": "meals"},
        {"id": 14, "name": "Kulhad Chai", "category_slug": "beverages"}
    ]
    predictions = model.predict_all_menu_demand(catalog)
    assert len(predictions) == 3
    # Check descending order by predicted demand
    assert predictions[0]["predicted_demand"] >= predictions[1]["predicted_demand"]
