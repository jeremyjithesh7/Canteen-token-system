import pytest
from fastapi.testclient import TestClient

def test_inventory_list_and_low_stock(client: TestClient, admin_auth_headers):
    response = client.get("/api/inventory/", headers=admin_auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    assert "current_stock" in items[0]
    assert "minimum_stock_alert" in items[0]

def test_restock_food_item(client: TestClient, admin_auth_headers):
    food_id = 1
    # Get current stock
    res_before = client.get("/api/inventory/", headers=admin_auth_headers)
    initial_stock = next(i["current_stock"] for i in res_before.json() if i["food_item_id"] == food_id)

    # Restock +25
    res_restock = client.put(
        f"/api/inventory/restock/{food_id}",
        json={"add_quantity": 25, "reason": "Fresh morning batch"},
        headers=admin_auth_headers
    )
    assert res_restock.status_code == 200
    assert res_restock.json()["current_stock"] == initial_stock + 25

def test_inventory_audit_logs(client: TestClient, admin_auth_headers):
    response = client.get("/api/inventory/logs", headers=admin_auth_headers)
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
