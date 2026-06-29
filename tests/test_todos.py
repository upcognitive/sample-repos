"""Todo management API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from orkest.api.app import create_app
from orkest.db.models import Base
from orkest.db.session import get_db

VALID_TODO = {"title": "Buy groceries"}


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


def test_create_todo(client: TestClient) -> None:
    response = client.post("/todos", json=VALID_TODO)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == VALID_TODO["title"]
    assert body["completed"] is False
    assert isinstance(body["id"], int)


def test_create_todo_with_completed(client: TestClient) -> None:
    response = client.post(
        "/todos",
        json={"title": "Finish report", "completed": True},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Finish report"
    assert body["completed"] is True


def test_create_todo_empty_title(client: TestClient) -> None:
    response = client.post("/todos", json={"title": "   "})
    assert response.status_code == 400
    assert response.json() == {"error": "Title must not be empty"}


def test_list_todos(client: TestClient) -> None:
    client.post("/todos", json={"title": "First todo"})
    client.post("/todos", json={"title": "Second todo"})

    response = client.get("/todos")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["title"] == "First todo"
    assert body[1]["title"] == "Second todo"


def test_list_todos_empty(client: TestClient) -> None:
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_get_todo_by_id(client: TestClient) -> None:
    created = client.post("/todos", json=VALID_TODO).json()
    response = client.get(f"/todos/{created['id']}")
    assert response.status_code == 200
    assert response.json() == {
        "id": created["id"],
        "title": VALID_TODO["title"],
        "completed": False,
    }


def test_get_todo_not_found(client: TestClient) -> None:
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found"}


def test_update_todo(client: TestClient) -> None:
    created = client.post("/todos", json=VALID_TODO).json()
    response = client.put(
        f"/todos/{created['id']}",
        json={"title": "Buy groceries and cook", "completed": True},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": created["id"],
        "title": "Buy groceries and cook",
        "completed": True,
    }


def test_update_todo_not_found(client: TestClient) -> None:
    response = client.put(
        "/todos/999",
        json={"title": "Updated title", "completed": False},
    )
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found"}


def test_update_todo_empty_title(client: TestClient) -> None:
    created = client.post("/todos", json=VALID_TODO).json()
    response = client.put(
        f"/todos/{created['id']}",
        json={"title": "   ", "completed": False},
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Title must not be empty"}


def test_delete_todo(client: TestClient) -> None:
    created = client.post("/todos", json=VALID_TODO).json()
    response = client.delete(f"/todos/{created['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/todos/{created['id']}")
    assert get_response.status_code == 404


def test_delete_todo_not_found(client: TestClient) -> None:
    response = client.delete("/todos/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Todo not found"}
