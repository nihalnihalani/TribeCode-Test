import pytest
from unittest.mock import MagicMock, patch
from src.agents.reddit_scout import RedditScout
from src.agents.twitter_scout import TwitterScout
from src.agents.interaction_agent import InteractionAgent
from src.database import Interaction

# --- RedditScout Tests ---

@pytest.fixture
def mock_praw(mock_env):
    with patch("src.agents.reddit_scout.praw.Reddit") as mock:
        yield mock

def test_reddit_scout_init(mock_praw, mock_env):
    """Test RedditScout initialization with credentials."""
    scout = RedditScout()
    assert scout.reddit is not None
    mock_praw.assert_called_once()

def test_reddit_scout_init_no_creds(monkeypatch):
    """Test RedditScout initialization without credentials."""
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    scout = RedditScout()
    assert scout.reddit is None

def test_reddit_fetch_posts(mock_praw, db_session, mock_env):
    """Test fetching posts from Reddit."""
    scout = RedditScout()
    
    # Mock subreddit search
    mock_subreddit = MagicMock()
    scout.reddit.subreddit.return_value = mock_subreddit
    
    # Mock submissions
    mock_submission = MagicMock()
    mock_submission.id = "post_123"
    mock_submission.title = "Test Post"
    mock_submission.selftext = "Test Content"
    mock_submission.url = "http://reddit.com/post_123"
    mock_submission.author = "test_author"
    
    mock_subreddit.search.return_value = [mock_submission]
    
    # Run fetch
    posts = scout.fetch_posts(["test_sub"], "query", limit=1)
    
    assert len(posts) == 1
    assert posts[0]["external_post_id"] == "post_123"
    assert posts[0]["title"] == "Test Post"
    
    # Verify saved to DB
    saved_posts = db_session.query(Interaction).all()
    assert len(saved_posts) == 1
    assert saved_posts[0].external_post_id == "post_123"
    assert saved_posts[0].platform == "Reddit"

def test_reddit_actions(mock_praw, mock_env):
    """Test like and comment actions."""
    scout = RedditScout()
    
    # Mock submission
    mock_submission = MagicMock()
    scout.reddit.submission.return_value = mock_submission
    
    # Test Like
    assert scout.like_post("123") is True
    mock_submission.upvote.assert_called_once()
    
    # Test Comment
    assert scout.comment_post("123", "Nice!") is True
    mock_submission.reply.assert_called_with("Nice!")

# --- TwitterScout Tests ---

@pytest.fixture
def mock_playwright():
    with patch("src.agents.twitter_scout.sync_playwright") as mock:
        yield mock

def test_twitter_fetch_posts(mock_playwright, db_session):
    """Test fetching posts from Twitter."""
    scout = TwitterScout()
    
    # Mock Context Manager
    mock_p = mock_playwright.return_value.__enter__.return_value
    mock_browser = mock_p.chromium.launch_persistent_context.return_value
    mock_page = mock_browser.new_page.return_value
    
    # Mock Elements
    mock_tweet = MagicMock()
    
    # Mock Time/Link element
    mock_time = MagicMock()
    mock_link_parent = MagicMock()
    mock_link_parent.get_attribute.return_value = "/user/status/tweet_456"
    mock_time.query_selector.return_value = mock_link_parent
    mock_tweet.query_selector.side_effect = lambda s: mock_time if s == 'time' else MagicMock()
    
    # Mock Text
    mock_text_el = MagicMock()
    mock_text_el.inner_text.return_value = "Hello Twitter"
    
    # Mock Author
    mock_user_el = MagicMock()
    mock_user_el.inner_text.return_value = "UserHandle"
    
    # Setup query_selector for tweet internals
    def tweet_query_selector(selector):
        if selector == 'time': return mock_time
        if selector == 'div[data-testid="tweetText"]': return mock_text_el
        if selector == 'div[data-testid="User-Name"]': return mock_user_el
        return None
    
    mock_tweet.query_selector.side_effect = tweet_query_selector
    
    # Return list of tweets
    mock_page.query_selector_all.return_value = [mock_tweet]
    
    # Run fetch
    posts = scout.fetch_posts(["keyword"], limit=1)
    
    assert len(posts) == 1
    assert posts[0]["id"] == "tweet_456"
    assert posts[0]["text"] == "Hello Twitter"
    
    # Verify saved to DB
    saved_posts = db_session.query(Interaction).all()
    assert len(saved_posts) == 1
    assert saved_posts[0].external_post_id == "tweet_456"
    assert saved_posts[0].platform == "Twitter"

# --- InteractionAgent Tests ---

@pytest.fixture
def mock_openai(mock_env):
    with patch("src.agents.interaction_agent.OpenAI") as mock:
        yield mock

def test_agent_generate_comment(mock_openai, mock_env):
    """Test generating a comment."""
    agent = InteractionAgent()
    
    # Mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Generated Comment"
    agent.client.chat.completions.create.return_value = mock_response
    
    target = Interaction(platform="Reddit", external_post_id="1", post_content="Target post")
    context = [Interaction(platform="Reddit", external_post_id="2", post_content="Context post")]
    
    comment = agent.generate_comment(target, context)
    
    assert comment == "Generated Comment"
    agent.client.chat.completions.create.assert_called_once()

def test_agent_no_key(monkeypatch):
    """Test agent without API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    agent = InteractionAgent()
    assert agent.client is None
    
    comment = agent.generate_comment(MagicMock(), [])
    assert "Error" in comment

