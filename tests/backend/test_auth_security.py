import pytest
from fastapi.testclient import TestClient

def test_refresh_token_issuance_and_rotation(client: TestClient):
    # 1. Login to get access & refresh tokens
    login_res = client.post("/api/auth/login", json={
        "email": "student@canteen.edu",
        "password": "Student@123"
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    old_refresh = data["refresh_token"]

    # 2. Call refresh endpoint
    refresh_res = client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_res.status_code == 200
    refreshed_data = refresh_res.json()
    assert "access_token" in refreshed_data
    assert "refresh_token" in refreshed_data
    new_refresh = refreshed_data["refresh_token"]
    assert new_refresh != old_refresh # Rotated!

    # 3. Old refresh token should now be rejected (revoked)
    stale_res = client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
    assert stale_res.status_code == 401

def test_login_rate_limiting(client: TestClient):
    bad_email = "ratelimit.test@canteen.edu"
    # Make 5 failed attempts
    for _ in range(5):
        client.post("/api/auth/login", json={"email": bad_email, "password": "WrongPassword"})

    # 6th attempt should be blocked with 429 Too Many Requests
    blocked_res = client.post("/api/auth/login", json={"email": bad_email, "password": "WrongPassword"})
    assert blocked_res.status_code == 429
    assert "Too many failed login attempts" in blocked_res.json()["detail"]
