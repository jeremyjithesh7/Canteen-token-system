import pytest

def test_crowd_forecast_api(client):
    """Test AI Crowd Forecast returns valid timeline and peak projections."""
    res = client.get("/api/ai/crowd-forecast")
    assert res.status_code == 200
    data = res.json()
    assert "current_crowd" in data
    assert "forecast_30m" in data
    assert "forecast_60m" in data
    assert "forecast_120m" in data
    assert "expected_peak_time" in data
    assert "expected_peak_level" in data
    assert "recommendation" in data

def test_inventory_intelligence_api(client, admin_auth_headers):
    """Test AI Inventory preparation recommendations."""
    res = client.get("/api/ai/inventory-intelligence?meal_slot=Lunch", headers=admin_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_items_analyzed" in data
    assert data["total_items_analyzed"] > 0
    assert "items" in data
    first_item = data["items"][0]
    assert "name" in first_item
    assert "current_stock" in first_item
    assert "predicted_demand" in first_item
    assert "recommended_preparation" in first_item
    assert "status" in first_item
