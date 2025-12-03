import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import Base

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh in-memory database for each test.
    Patches src.database.SessionLocal to use this session.
    """
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Patch the SessionLocal in src.database to return our test session
    # We need to patch it so that when src.database functions call SessionLocal(), they get our session.
    # However, SessionLocal is a class/callable. We should patch it to return our session.
    # But wait, SessionLocal() creates a *new* session. 
    # If we want to share the SAME session (for in-memory DB to work across calls if not careful), 
    # or at least the same ENGINE.
    
    # Better approach: Patch 'src.database.SessionLocal' to be a factory that returns our `session` 
    # OR shares the engine.
    # Since we want to verify data committed, we should probably share the engine.
    
    # Let's try patching the engine first, but src.database creates engine at module level.
    # So we patch the objects in src.database.
    
    with patch("src.database.engine", engine), \
         patch("src.database.SessionLocal", Session):
        yield session

    # Teardown
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def mock_env(monkeypatch):
    """Sets up environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("REDDIT_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "test-agent")
    monkeypatch.setenv("REDDIT_USERNAME", "test-user")
    monkeypatch.setenv("REDDIT_PASSWORD", "test-pass")
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)

