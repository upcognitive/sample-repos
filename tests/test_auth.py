"""Authentication tests."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from orkest.api.app import create_app
from orkest.db.models import Base, ClientCredential
from orkest.db.session import get_db

TEST_CLIENT_ID = "test-client"
TEST_CLIENT_SECRET = "test-secret"


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(
        ClientCredential(
            client_id=TEST_CLIENT_ID,
            client_secret=TEST_CLIENT_SECRET,
            name="Test Client",
        )
    )
    db.commit()
    db.close()

    app = create_app()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    os.environ["ORKEST_JWT_SECRET"] = "test-secret-key-with-sufficient-length"
    with TestClient(app) as test_client:
        yield test_client


def test_token_endpoint_returns_jwt(client: TestClient) -> None:
    response = client.post(
        "/auth/token",
        json={"client_id": TEST_CLIENT_ID, "client_secret": TEST_CLIENT_SECRET},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_token_endpoint_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/auth/token",
        json={"client_id": TEST_CLIENT_ID, "client_secret": "wrong-secret"},
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_auth(client: TestClient) -> None:
    response = client.get("/agents/")
    assert response.status_code == 401


def test_protected_endpoint_accepts_valid_token(client: TestClient) -> None:
    token_response = client.post(
        "/auth/token",
        json={"client_id": TEST_CLIENT_ID, "client_secret": TEST_CLIENT_SECRET},
    )
    access_token = token_response.json()["access_token"]

    response = client.get(
        "/agents/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"client_id": TEST_CLIENT_ID, "agents": []}
