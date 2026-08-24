import pytest

def test_get_my_rewards(client, student_auth_headers):
    """Test retrieving rewards summary, streak, tier, and achievements."""
    res = client.get("/api/rewards/me", headers=student_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_points" in data
    assert "tier" in data
    assert "current_streak_days" in data
    assert "achievements" in data
    assert isinstance(data["achievements"], list)

def test_rewards_leaderboard(client, student_auth_headers):
    """Test campus leaderboard ranking and points."""
    res = client.get("/api/rewards/leaderboard", headers=student_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "top_users" in data
    assert len(data["top_users"]) > 0
    first_rank = data["top_users"][0]
    assert first_rank["rank"] == 1
    assert "user_name" in first_rank
    assert "total_points" in first_rank
    assert "streak_days" in first_rank

def test_rewards_points_accrual_on_order(client, student_auth_headers):
    """Test placing an order increments student reward points."""
    rew_before = client.get("/api/rewards/me", headers=student_auth_headers).json()["total_points"]

    order_payload = {
        "items": [{"food_item_id": 2, "quantity": 2}],
        "payment_method": "UPI",
        "notes": "Testing points accrual"
    }
    order_res = client.post("/api/orders/", json=order_payload, headers=student_auth_headers)
    assert order_res.status_code == 201

    rew_after = client.get("/api/rewards/me", headers=student_auth_headers).json()["total_points"]
    assert rew_after >= rew_before
