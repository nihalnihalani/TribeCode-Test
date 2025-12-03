import pytest
import os
from unittest.mock import MagicMock, patch
from src.agents.twitter_scout import TwitterScout

def test_twitter_scout_initialization():
    scout = TwitterScout()
    assert "twitter_auth_data" in scout.user_data_dir
    assert scout.headless is True

@patch('src.agents.twitter_scout.sync_playwright')
def test_fetch_posts_mock(mock_playwright):
    """Test fetch_posts logic with mocked Playwright to avoid actual browser launch in CI/Test env."""
    scout = TwitterScout()
    
    # Mock the context manager and browser
    mock_p = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_p
    mock_browser = MagicMock()
    mock_p.chromium.launch_persistent_context.return_value = mock_browser
    mock_page = mock_browser.new_page.return_value
    
    # Mock elements
    mock_page.query_selector_all.return_value = [] # Return empty for simplicity
    
    results = scout.fetch_posts(["test"])
    
    assert results == []
    mock_page.goto.assert_called()
    assert "twitter.com/search" in mock_page.goto.call_args[0][0]

@patch('src.agents.twitter_scout.sync_playwright')
def test_like_post_mock(mock_playwright):
    """Test like_post logic with mocked Playwright."""
    scout = TwitterScout()
    
    mock_p = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_p
    mock_browser = MagicMock()
    mock_p.chromium.launch_persistent_context.return_value = mock_browser
    mock_page = mock_browser.new_page.return_value
    
    # Mock success
    mock_like_btn = MagicMock()
    mock_page.wait_for_selector.return_value = mock_like_btn
    
    result = scout.like_post("12345")
    
    assert result is True
    mock_like_btn.click.assert_called()

@patch('src.agents.twitter_scout.sync_playwright')
def test_fetch_and_save_db(mock_playwright, tmp_path):
    """Integration test: Scout fetches a tweet and saves it to DB."""
    # Setup temporary DB
    import src.database
    # Use a temp db file
    db_path = tmp_path / "test_vibebot.db"
    # Patch the engine/session in database.py? 
    # Easier to just point the DATABASE_URL env var or monkeypatch.
    # But database.py creates engine at module level. We might need to reload or mock.
    
    # Let's just mock save_interaction to return True, 
    # OR better, verify save_interaction is called with correct params.
    # We already tested DB logic in test_db.py (presumably).
    # Let's stick to mocking save_interaction to verify integration flow.
    
    with patch('src.agents.twitter_scout.save_interaction') as mock_save:
        scout = TwitterScout()
        
        # Mock Browser
        mock_p = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_p
        mock_page = mock_p.chromium.launch_persistent_context.return_value.new_page.return_value
        
        # Mock Tweet Element
        mock_tweet = MagicMock()
        
        # Setup selectors to return data
        # Time element for ID
        mock_time = MagicMock()
        mock_parent = MagicMock()
        mock_parent.get_attribute.return_value = "/user/status/123456"
        mock_time.query_selector.return_value = mock_parent
        mock_tweet.query_selector.side_effect = lambda s: mock_time if s == 'time' else (
            MagicMock(inner_text=lambda: "Hello World") if "tweetText" in s else (
            MagicMock(inner_text=lambda: "User1") if "User-Name" in s else None
            )
        )
        
        mock_page.query_selector_all.return_value = [mock_tweet]
        
        scout.fetch_posts(["test"])
        
        mock_save.assert_called_once()
        args = mock_save.call_args[1]
        assert args['platform'] == "Twitter"
        assert args['external_post_id'] == "123456"
        assert args['post_content'] == "Hello World"


