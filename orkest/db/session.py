"""Database session management."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from orkest.db.models import Base

DEFAULT_DATABASE_URL = "sqlite:///./orkest.db"

engine = create_engine(
    os.environ.get("ORKEST_DATABASE_URL", DEFAULT_DATABASE_URL),
    connect_args={"check_same_thread": False}
    if os.environ.get("ORKEST_DATABASE_URL", DEFAULT_DATABASE_URL).startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session]:
    """Yield a database session for request-scoped use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
