import pytest
from fastapi.testclient import TestClient

def test_cart_lifecycle(client: TestClient, student_auth_headers):
    # 1. Start with clear cart
    del_res = client.delete("/api/cart/", headers=student_auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["total_items_count"] == 0

    # 2. Add Masala Dosa (id=1, qty=2)
    add_res = client.post("/api/cart/items", json={
        "food_item_id": 1,
        "quantity": 2,
        "special_notes": "Extra crispy"
    }, headers=student_auth_headers)
    assert add_res.status_code == 200
    cart = add_res.json()
    assert cart["total_items_count"] == 2
    assert len(cart["items"]) == 1
    assert cart["items"][0]["name"] == "Masala Dosa"
    assert cart["items"][0]["quantity"] == 2

    # 3. Add Filter Coffee (id=19, qty=1)
    add_res2 = client.post("/api/cart/items", json={
        "food_item_id": 19,
        "quantity": 1,
        "special_notes": "Strong"
    }, headers=student_auth_headers)
    assert add_res2.status_code == 200
    cart2 = add_res2.json()
    assert cart2["total_items_count"] == 3
    assert len(cart2["items"]) == 2
    assert float(cart2["grand_total"]) > 0

    # 4. Sync client cart
    sync_res = client.post("/api/cart/sync", json={
        "items": [
            {"food_item_id": 4, "quantity": 3, "special_notes": "Warm idlis"}
        ]
    }, headers=student_auth_headers)
    assert sync_res.status_code == 200
    synced = sync_res.json()
    assert synced["total_items_count"] == 3
    assert synced["items"][0]["food_item_id"] == 4

    # 5. Remove item
    rem_res = client.delete("/api/cart/items/4", headers=student_auth_headers)
    assert rem_res.status_code == 200
    assert rem_res.json()["total_items_count"] == 0
