import pytest
from fastapi.testclient import TestClient

def test_student_login_success(client: TestClient):
    response = client.post("/api/auth/login", json={
        "email": "student@canteen.edu",
        "password": "Student@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "student@canteen.edu"
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
        "email": "student@canteen.edu",
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
    assert data["email"] == "student@canteen.edu"
