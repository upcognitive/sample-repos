"""Pydantic schemas for todo management."""

from pydantic import BaseModel, field_validator


class CreateTodoRequest(BaseModel):
    title: str
    completed: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title must not be empty")
        return value


class UpdateTodoRequest(BaseModel):
    title: str
    completed: bool

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title must not be empty")
        return value


class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = {"from_attributes": True}
