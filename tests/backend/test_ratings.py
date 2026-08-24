import pytest
from fastapi.testclient import TestClient

def test_submit_food_rating(client: TestClient, student_auth_headers):
    # 1. Submit rating for Masala Dosa (id=1)
    payload = {
        "food_item_id": 1,
        "rating": 5,
        "comment": "Crispy golden perfection, best dosa on campus!"
    }
    res = client.post("/api/ratings/", json=payload, headers=student_auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["food_item_id"] == 1
    assert data["rating"] == 5
    assert data["comment"] == payload["comment"]

    # 2. Get reviews summary
    sum_res = client.get("/api/ratings/dish/1")
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert summary["food_item_id"] == 1
    assert summary["average_rating"] >= 4.0
    assert summary["rating_count"] >= 1
    assert len(summary["latest_reviews"]) >= 1

def test_invalid_rating_rejected(client: TestClient, student_auth_headers):
    # Rating must be between 1 and 5
    payload = {
        "food_item_id": 1,
        "rating": 6 # Invalid!
    }
    res = client.post("/api/ratings/", json=payload, headers=student_auth_headers)
    assert res.status_code == 422
