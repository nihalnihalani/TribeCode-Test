import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, Interaction, save_interaction, check_deduplication, get_all_interactions

# Use an in-memory SQLite DB for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Monkeypatch the SessionLocal in src.database for the context of the test if we were calling it directly,
    # but since we are calling helper functions that instantiate their own SessionLocal, 
    # we might need to override the DATABASE_URL env var or similar.
    # For simplicity in this MVP script, I'll test the logic by temporarily pointing the src.database engine to memory 
    # OR just test the logic using the helpers if I can configure them.
    
    # Actually, the easiest way to test `save_interaction` which uses `SessionLocal` internally 
    # is to make sure `src.database` uses our test DB. 
    # Since `src.database` initializes `engine` at module level, we can't easily swap it without reloading.
    # 
    # Strategy: We will just test the logic flow by mocking or just running it against a temp file db.
    # For this environment, let's just use a temp file db.
    
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_save_and_retrieve_interaction():
    # We'll use the actual file-based DB logic from src.database but with a test-specific name if possible,
    # but `src.database` hardcodes env var loading. 
    # Let's just rely on the fact that we can use the functions directly.
    # We'll manually initialize the DB in the test setup.
    
    # Initialize DB (this might create vibebot.db in the root if not careful, which is fine for MVP)
    from src.database import init_db, SessionLocal
    init_db()
    
    # Clear table to be safe (if using persistent DB)
    s = SessionLocal()
    s.query(Interaction).delete()
    s.commit()
    s.close()

    # Test Save
    save_interaction(
        platform="Reddit",
        external_post_id="test_post_123",
        post_content="This is a test post",
        status="ARCHIVED"
    )

    # Test Deduplication
    assert check_deduplication("test_post_123") is True
    assert check_deduplication("non_existent_id") is False

    # Test Retrieval
    interactions = get_all_interactions()
    assert len(interactions) >= 1
    assert interactions[0].external_post_id == "test_post_123"
    assert interactions[0].post_content == "This is a test post"


