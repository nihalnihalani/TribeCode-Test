import pytest
from src.database import Interaction, save_interaction, check_deduplication, get_all_interactions

def test_save_interaction(db_session):
    """Test saving a new interaction."""
    interaction = save_interaction(
        platform="Reddit",
        external_post_id="post_123",
        post_content="Test content",
        status="ARCHIVED"
    )
    
    assert interaction.id is not None
    assert interaction.platform == "Reddit"
    assert interaction.external_post_id == "post_123"
    assert interaction.status == "ARCHIVED"

def test_save_duplicate_interaction(db_session):
    """Test that saving a duplicate interaction returns the existing one."""
    # Save first time
    first = save_interaction(
        platform="Reddit",
        external_post_id="post_duplicate",
        post_content="Original content"
    )
    
    # Save second time
    second = save_interaction(
        platform="Reddit",
        external_post_id="post_duplicate",
        post_content="New content" # Should be ignored or updated depending on logic
    )
    
    assert first.id == second.id
    # Based on current implementation, it returns existing without updating if found
    assert second.post_content == "Original content"

def test_check_deduplication(db_session):
    """Test deduplication check."""
    save_interaction("Twitter", "tweet_1", "content")
    
    assert check_deduplication("tweet_1") is True
    assert check_deduplication("tweet_2") is False

def test_get_all_interactions(db_session):
    """Test retrieving all interactions."""
    save_interaction("Reddit", "r1", "content")
    save_interaction("Twitter", "t1", "content")
    
    interactions = get_all_interactions()
    assert len(interactions) == 2
    # Ordered by created_at desc
    assert interactions[0].external_post_id == "t1"
    assert interactions[1].external_post_id == "r1"

def test_save_interaction_error_handling(db_session, mocker):
    """Test error handling during save."""
    # Mock session.commit to raise exception
    # We need to mock the session inside save_interaction.
    # Since save_interaction instantiates SessionLocal(), and we patched SessionLocal in conftest,
    # we can mock the session returned by SessionLocal.
    
    # However, db_session fixture already patches SessionLocal to return a working session class.
    # To force an error, we might need to mock the commit method of the session instance that SessionLocal() returns.
    
    from sqlalchemy.exc import SQLAlchemyError
    
    # Create a mock session that raises error on commit
    mock_session = mocker.MagicMock()
    mock_session.commit.side_effect = SQLAlchemyError("DB Error")
    mock_session.query.return_value.filter_by.return_value.first.return_value = None # No existing record
    
    # Patch SessionLocal to return this mock session
    # Note: conftest patches SessionLocal to return the real Session class. 
    # We need to override that patch or patch over it.
    with mocker.patch("src.database.SessionLocal", return_value=mock_session):
        with pytest.raises(SQLAlchemyError):
            save_interaction("Reddit", "error_post", "content")
