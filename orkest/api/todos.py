"""Todo management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from orkest.api.schemas.todos import CreateTodoRequest, TodoResponse, UpdateTodoRequest
from orkest.db.models import Todo
from orkest.db.session import get_db

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    body: CreateTodoRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Todo:
    """Create a new todo."""
    todo = Todo(title=body.title, completed=body.completed)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.get("", response_model=list[TodoResponse])
def list_todos(
    db: Annotated[Session, Depends(get_db)],
) -> list[Todo]:
    """Get all todos."""
    return db.query(Todo).order_by(Todo.id).all()


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Todo:
    """Get a specific todo by ID."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Todo not found"},
        )
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    body: UpdateTodoRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Todo:
    """Update a specific todo."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Todo not found"},
        )

    todo.title = body.title
    todo.completed = body.completed
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete a specific todo."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Todo not found"},
        )

    db.delete(todo)
    db.commit()
