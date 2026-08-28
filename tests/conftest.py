import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.database.base import Base
from backend.app.database.session import get_db
import backend.app.models # Register all models in Base.metadata
from backend.app.utils.seed_data import seed_database_if_empty

# In-memory test SQLite database with StaticPool so all connections share the same memory DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def db_session():
    """Initializes tables and seeds initial data once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database_if_empty(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient with overridden database session dependency."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def student_auth_headers(client):
    """Dynamically registers a student and returns Authorization header."""
    client.post("/api/auth/register", json={
        "name": "Test Student",
        "email": "teststudent@canteen.edu",
        "password": "Student@123",
        "phone": "+1-555-9999",
        "department": "Computer Science"
    })
    res = client.post("/api/auth/login", json={"email": "teststudent@canteen.edu", "password": "Student@123"})
    assert res.status_code == 200, f"Student login failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="session")
def admin_auth_headers(client):
    """Logs in as demo admin and returns Authorization header."""
    res = client.post("/api/auth/login", json={"email": "admin@canteen.edu", "password": "Admin@123"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="session")
def staff_auth_headers(client):
    """Logs in as demo staff and returns Authorization header."""
    res = client.post("/api/auth/login", json={"email": "staff@canteen.edu", "password": "Staff@123"})
    assert res.status_code == 200, f"Staff login failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
