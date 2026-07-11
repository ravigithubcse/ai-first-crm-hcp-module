# =============================================================================
# AI-First CRM HCP Module - Pytest Configuration
# =============================================================================
# Author  : Ravi Kumar
# Version : 1.0.0
# Points the app at a throwaway SQLite file for the test session (instead of
# the real Postgres in .env) and sets a placeholder Groq key so modules that
# construct a ChatGroq client at call time don't fail on import. Must set
# these env vars before any `app.*` module is imported, since settings are
# read once at import time.
# =============================================================================
import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).parent / "_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ.setdefault("GROQ_API_KEY", "test-placeholder-key")

import pytest  # noqa: E402

from app.core.database import Base, engine  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_schema():
    """Recreate all tables before every test for isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def pytest_sessionfinish(session, exitstatus):
    TEST_DB_PATH.unlink(missing_ok=True)
