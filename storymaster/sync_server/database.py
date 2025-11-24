"""Database session management for the sync server"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from storymaster.sync_server.config import config

# Create engine
engine = create_engine(
    config.get_database_url(),
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    Automatically handles session lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
