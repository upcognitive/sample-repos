"""Pydantic schemas for user management."""

from pydantic import BaseModel, EmailStr, field_validator


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        return value


class UpdateUserPasswordRequest(BaseModel):
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}
