"""User management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from orkest.api.schemas.users import (
    CreateUserRequest,
    UpdateUserPasswordRequest,
    UserResponse,
)
from orkest.db.models import User
from orkest.db.session import get_db
from orkest.security.password import hash_password, validate_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: CreateUserRequest,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Create a new user."""
    password_error = validate_password(body.password)
    if password_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": password_error},
        )

    existing_user = (
        db.query(User)
        .filter((User.email == body.email) | (User.username == body.username))
        .first()
    )
    if existing_user is not None:
        if existing_user.email == body.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Email already exists"},
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Username already exists"},
        )

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_password(
    user_id: int,
    body: UpdateUserPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Update the password for an existing user."""
    password_error = validate_password(body.password)
    if password_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": password_error},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "User not found"},
        )

    user.password_hash = hash_password(body.password)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Find a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "User not found"},
        )
    return user


@router.get("", response_model=UserResponse)
def get_user_by_email(
    email: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Find a user by email."""
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "User not found"},
        )
    return user
