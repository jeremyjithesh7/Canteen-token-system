import pytest
from fastapi.testclient import TestClient

def test_initial_dish_has_zero_reviews(client: TestClient):
    """Verifies that an unreviewed dish starts with 0 reviews and None average rating."""
    res = client.get("/api/ratings/dish/5") # Medu Vada
    assert res.status_code == 200
    data = res.json()
    assert data["food_item_id"] == 5
    assert data["average_rating"] is None
    assert data["rating_count"] == 0
    assert data["star_counts"] == {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0} or data["star_counts"] == {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    assert len(data["latest_reviews"]) == 0

def test_unpurchased_item_rating_rejected(client: TestClient):
    """Verifies that a student cannot rate a dish they have not ordered/completed."""
    email = "noratingorders@canteen.edu"
    client.post("/api/auth/register", json={
        "email": email,
        "name": "No Orders Student",
        "password": "Password123!",
        "role_id": 3
    })
    login_res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/ratings/", json={
        "food_item_id": 14, # Mysore Pak (not purchased)
        "rating": 5,
        "comment": "Tasted great"
    }, headers=headers)
    assert res.status_code == 403
    assert "You can only rate dishes you have ordered" in res.json()["detail"]

def test_submit_food_rating_after_order(client: TestClient, student_auth_headers):
    # 1. First top up and order Masala Dosa (id=1) with Wallet so it is Confirmed
    client.post("/api/wallet/topup", json={"amount": 100.0, "payment_method": "UPI"}, headers=student_auth_headers)
    order_res = client.post("/api/orders/", json={
        "items": [{"food_item_id": 1, "quantity": 1}],
        "payment_method": "Wallet"
    }, headers=student_auth_headers)
    assert order_res.status_code == 201
    order_id = order_res.json()["id"]

    # 2. Submit genuine rating
    payload = {
        "food_item_id": 1,
        "order_id": order_id,
        "rating": 5,
        "comment": "Crispy golden perfection, authentic taste!"
    }
    res = client.post("/api/ratings/", json=payload, headers=student_auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["food_item_id"] == 1
    assert data["rating"] == 5
    assert data["comment"] == payload["comment"]

    # 3. Get reviews summary
    sum_res = client.get("/api/ratings/dish/1")
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert summary["food_item_id"] == 1
    assert float(summary["average_rating"]) == 5.0
    assert summary["rating_count"] == 1
    assert len(summary["latest_reviews"]) == 1

def test_invalid_rating_rejected(client: TestClient, student_auth_headers):
    # Rating must be between 1 and 5
    payload = {
        "food_item_id": 1,
        "rating": 6 # Invalid!
    }
    res = client.post("/api/ratings/", json=payload, headers=student_auth_headers)
    assert res.status_code == 422
