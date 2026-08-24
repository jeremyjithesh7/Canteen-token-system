import pytest
from fastapi.testclient import TestClient

def test_get_categories(client: TestClient):
    response = client.get("/api/food/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    category_slugs = [c["slug"] for c in data]
    assert "south-indian-tiffin-meals" in category_slugs
    assert "desserts" in category_slugs
    assert "beverages" in category_slugs

def test_get_food_items_catalog(client: TestClient):
    response = client.get("/api/food/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 25
    # Verify properties
    first = items[0]
    assert "name" in first
    assert "price" in first
    assert "prep_time_minutes" in first
    assert "current_stock" in first

def test_filter_food_items_by_veg(client: TestClient):
    response = client.get("/api/food/items?is_veg=true")
    assert response.status_code == 200
    veg_items = response.json()
    assert all(item["is_veg"] is True for item in veg_items)

def test_admin_create_food_item(client: TestClient, admin_auth_headers):
    new_dish = {
        "name": "Chef Special Podi Masala Dosa",
        "category_id": 1,
        "counter_id": 1,
        "description": "Crisp dosa roasted in spiced gun powder and ghee",
        "price": 85.00,
        "prep_time_minutes": 8,
        "is_veg": True,
        "is_vegan": False,
        "is_available": True,
        "initial_stock": 40
    }
    response = client.post("/api/food/items", json=new_dish, headers=admin_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == new_dish["name"]
    assert data["current_stock"] == 40

def test_non_admin_cannot_create_food_item(client: TestClient, student_auth_headers):
    dish = {
        "name": "Unauthorized Dish",
        "category_id": 1,
        "price": 50.00
    }
    response = client.post("/api/food/items", json=dish, headers=student_auth_headers)
    assert response.status_code == 403
