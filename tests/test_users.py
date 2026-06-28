"""User management API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from orkest.api.app import create_app
from orkest.db.models import Base
from orkest.db.session import get_db

VALID_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "pass1!",
}


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    app = create_app()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


def test_create_user(client: TestClient) -> None:
    response = client.post("/users", json=VALID_USER)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == VALID_USER["username"]
    assert body["email"] == VALID_USER["email"]
    assert "password" not in body
    assert isinstance(body["id"], int)


def test_create_user_missing_email(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={"username": "testuser", "password": "pass1!"},
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Missing email on the request body"}


def test_create_user_invalid_username(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "username": "ab",
            "email": "short@example.com",
            "password": "pass1!",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Username must be at least 3 characters"}


def test_create_user_invalid_password(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "weak@example.com",
            "password": "weak",
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": "Password must be at least 6 characters and include numbers and special characters",
    }


def test_create_user_duplicate_email(client: TestClient) -> None:
    client.post("/users", json=VALID_USER)
    response = client.post(
        "/users",
        json={
            "username": "anotheruser",
            "email": VALID_USER["email"],
            "password": "pass1!",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Email already exists"}


def test_get_user_by_id(client: TestClient) -> None:
    created = client.post("/users", json=VALID_USER).json()
    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 200
    assert response.json() == {
        "id": created["id"],
        "username": VALID_USER["username"],
        "email": VALID_USER["email"],
    }


def test_get_user_by_email(client: TestClient) -> None:
    created = client.post("/users", json=VALID_USER).json()
    response = client.get("/users", params={"email": VALID_USER["email"]})
    assert response.status_code == 200
    assert response.json() == {
        "id": created["id"],
        "username": VALID_USER["username"],
        "email": VALID_USER["email"],
    }


def test_get_user_not_found(client: TestClient) -> None:
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"error": "User not found"}


def test_update_user_password(client: TestClient) -> None:
    created = client.post("/users", json=VALID_USER).json()
    response = client.patch(
        f"/users/{created['id']}",
        json={"password": "newpass1!"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_user_password_not_found(client: TestClient) -> None:
    response = client.patch("/users/999", json={"password": "newpass1!"})
    assert response.status_code == 404
    assert response.json() == {"error": "User not found"}
