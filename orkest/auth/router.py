"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from orkest.auth.jwt import create_access_token
from orkest.db.models import ClientCredential
from orkest.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/token", response_model=TokenResponse)
def create_token(
    body: TokenRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Generate a JWT access token from valid client credentials."""
    client = (
        db.query(ClientCredential)
        .filter(ClientCredential.client_id == body.client_id)
        .first()
    )
    if client is None or client.client_secret != body.client_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    access_token = create_access_token(client.client_id)
    return TokenResponse(access_token=access_token)
