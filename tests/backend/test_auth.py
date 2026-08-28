import pytest
from fastapi.testclient import TestClient

def test_student_login_success(client: TestClient):
    client.post("/api/auth/register", json={
        "name": "Auth Student",
        "email": "auth.student@canteen.edu",
        "password": "Student@123",
        "phone": "+1-555-7766",
        "department": "IT"
    })
    response = client.post("/api/auth/login", json={
        "email": "auth.student@canteen.edu",
        "password": "Student@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "auth.student@canteen.edu"
    assert data["user"]["role_id"] == 3

def test_admin_login_success(client: TestClient):
    response = client.post("/api/auth/login", json={
        "email": "admin@canteen.edu",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role_id"] == 1

def test_invalid_login_credentials(client: TestClient):
    response = client.post("/api/auth/login", json={
        "email": "admin@canteen.edu",
        "password": "WrongPassword!99"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_user_registration_and_duplicate_check(client: TestClient):
    new_email = "test.student@canteen.edu"
    # 1. Register new user
    res1 = client.post("/api/auth/register", json={
        "name": "Test Student",
        "email": new_email,
        "phone": "+1-555-9988",
        "department": "Civil Eng",
        "password": "SecurePassword@123"
    })
    assert res1.status_code == 201
    assert res1.json()["user"]["email"] == new_email

    # 2. Duplicate registration attempt
    res2 = client.post("/api/auth/register", json={
        "name": "Duplicate Student",
        "email": new_email,
        "password": "SecurePassword@123"
    })
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

def test_get_current_user_profile(client: TestClient, student_auth_headers):
    response = client.get("/api/auth/me", headers=student_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "teststudent@canteen.edu"

    # Test /api/users/me alias
    res_user = client.get("/api/users/me", headers=student_auth_headers)
    assert res_user.status_code == 200
    assert res_user.json()["email"] == "teststudent@canteen.edu"

def test_user_preferences_lifecycle(client: TestClient, student_auth_headers):
    """Test reading and updating dietary preferences."""
    # Update preferences
    put_res = client.put("/api/users/me/preferences", json={
        "is_veg_only": True,
        "spice_level": "Spicy",
        "dietary_notes": "No peanuts please"
    }, headers=student_auth_headers)
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["is_veg_only"] is True
    assert data["spice_level"] == "Spicy"
    assert data["dietary_notes"] == "No peanuts please"

    # Retrieve preferences
    get_res = client.get("/api/users/me/preferences", headers=student_auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["is_veg_only"] is True
