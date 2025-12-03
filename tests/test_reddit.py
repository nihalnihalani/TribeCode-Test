import pytest
from unittest.mock import MagicMock, patch
from src.agents.reddit_scout import RedditScout

@pytest.fixture
def mock_reddit():
    with patch('praw.Reddit') as mock:
        yield mock

def test_reddit_fetch_posts(mock_reddit):
    # Setup Mock
    mock_instance = mock_reddit.return_value
    mock_subreddit = MagicMock()
    mock_instance.subreddit.return_value = mock_subreddit
    
    # Mock submission
    mock_submission = MagicMock()
    mock_submission.id = "test_id_1"
    mock_submission.title = "Build in Public Test"
    mock_submission.selftext = "Test Content"
    mock_submission.url = "http://reddit.com/test"
    mock_submission.author = "test_author"
    
    mock_subreddit.search.return_value = [mock_submission]

        # Initialize Scout (will use mocked PRAW)
        scout = RedditScout()
        
        # Fix: We must ensure self.reddit is set, otherwise fetch_posts returns [] immediately
        # The previous logic in __init__ might fail if env vars are missing during test.
        # But since we mocked praw.Reddit, it might have succeeded. 
        # However, we added a check `if not self.reddit:` in fetch_posts.
        # Let's verify `scout.reddit` is set.
        if not scout.reddit:
            scout.reddit = mock_instance # Force inject mock if init failed

        # Run Fetch
        # We need to mock check_deduplication to always return False (not duplicate) for this test
        with patch('src.agents.reddit_scout.check_deduplication', return_value=False):
            with patch('src.agents.reddit_scout.save_interaction') as mock_save:
                results = scout.fetch_posts(["saas"], limit=1)
                
                assert len(results) == 1
                assert results[0]['title'] == "Build in Public Test"
                mock_save.assert_called_once()

def test_reddit_like_post(mock_reddit):
    mock_instance = mock_reddit.return_value
    mock_submission = MagicMock()
    mock_instance.submission.return_value = mock_submission
    
    scout = RedditScout()
    # Must mock that scout.reddit is not None for like to proceed
    scout.reddit = mock_instance
    
    success = scout.like_post("test_id_1")
    
    assert success is True
    mock_submission.upvote.assert_called_once()
