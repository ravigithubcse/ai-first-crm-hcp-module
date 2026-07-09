# =============================================================================
# AI-First CRM HCP Module - Database Module
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : SQLAlchemy database configuration and session management
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Database configuration using SQLAlchemy with PostgreSQL.
Provides session management and connection handling.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency to get a database session.
    Automatically closes the session after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize the database by creating all tables."""
    from app.models import hcp, interaction, follow_up  # noqa: F401
    Base.metadata.create_all(bind=engine)