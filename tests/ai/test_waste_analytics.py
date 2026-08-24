import pytest

def test_food_waste_analytics_api(client, admin_auth_headers):
    """Test AI Food Waste Analytics returns financial loss and reduction tips."""
    res = client.get("/api/ai/waste-analytics", headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "overall_waste_percentage" in data
    assert "total_financial_loss_inr" in data
    assert float(data["total_financial_loss_inr"]) >= 0.0
    assert "most_wasted_dishes" in data
    assert "weekly_trend" in data
    assert "ai_waste_reduction_suggestions" in data
    assert len(data["ai_waste_reduction_suggestions"]) > 0

def test_ai_recommendations_match_percentage(client, student_auth_headers):
    """Test upgraded AI recommendations contain match_percentage and confidence tags."""
    res = client.get("/api/ai/recommendations?top_n=4", headers=student_auth_headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    first = items[0]
    assert "match_percentage" in first
    assert 50 <= first["match_percentage"] <= 100
    assert "recommendation_reason" in first
    assert len(first["recommendation_reason"]) > 0
