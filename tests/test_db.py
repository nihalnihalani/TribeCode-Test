import pytest
from src.database import Interaction, save_interaction, check_deduplication, get_all_interactions

def test_save_interaction(db_session):
    """Test saving a new interaction."""
    interaction = save_interaction(
        platform="Twitter",
        external_post_id="post_123",
        post_content="Test content",
        status="ARCHIVED"
    )
    
    assert interaction.id is not None
    assert interaction.platform == "Twitter"
    assert interaction.external_post_id == "post_123"
    assert interaction.status == "ARCHIVED"

def test_save_duplicate_interaction(db_session):
    """Test that saving a duplicate interaction returns the existing one."""
    # Save first time
    first = save_interaction(
        platform="Twitter",
        external_post_id="post_duplicate",
        post_content="Original content"
    )
    
    # Save second time
    second = save_interaction(
        platform="Twitter",
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
    save_interaction("Twitter", "r1", "content")
    save_interaction("Twitter", "t1", "content")
    
    interactions = get_all_interactions()
    assert len(interactions) == 2
    # Ordered by created_at desc
    assert interactions[0].external_post_id == "t1"
    assert interactions[1].external_post_id == "r1"

def test_save_interaction_error_handling(db_session):
    """Test error handling during save."""
    # Mock session.commit to raise exception
    from sqlalchemy.exc import SQLAlchemyError
    from unittest.mock import patch, MagicMock
    
    # Create a mock session that raises error on commit
    mock_session = MagicMock()
    mock_session.commit.side_effect = SQLAlchemyError("DB Error")
    mock_session.query.return_value.filter_by.return_value.first.return_value = None # No existing record
    
    # Patch SessionLocal to return this mock session
    with patch("src.database.SessionLocal", return_value=mock_session):
        with pytest.raises(SQLAlchemyError):
            save_interaction("Twitter", "error_post", "content")
