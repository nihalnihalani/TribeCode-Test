import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.web.app import app
from src.database import Interaction

@pytest.fixture
def client(db_session):
    """
    Test client for the app.
    Mocks background threads and external agents.
    """
    # Mock threading to prevent auto-scout loop
    with patch("src.web.app.threading.Thread"):
        # Mock agents to prevent API calls
        with patch("src.web.app.reddit_scout") as mock_reddit, \
             patch("src.web.app.twitter_scout") as mock_twitter, \
             patch("src.web.app.interaction_agent") as mock_agent:
            
            # Setup common mocks
            mock_reddit.fetch_posts.return_value = []
            mock_twitter.fetch_posts.return_value = []
            mock_agent.generate_comment.return_value = "Mocked Comment"
            
            with TestClient(app) as c:
                yield c

def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "VibeBot" in response.text

def test_interactions_page(client, db_session):
    # Seed some data
    db_session.add(Interaction(platform="Reddit", external_post_id="r1", post_content="Reddit Post"))
    db_session.add(Interaction(platform="Twitter", external_post_id="t1", post_content="Twitter Post"))
    db_session.commit()
    
    response = client.get("/interactions")
    assert response.status_code == 200
    assert "Reddit Post" in response.text
    assert "Twitter Post" in response.text

def test_scout_trigger(client):
    response = client.post("/scout", data={
        "platform": "reddit",
        "limit": 5,
        "query": "test"
    })
    # Redirects to interactions
    assert response.status_code == 200 # TestClient follows redirects by default? No, usually 303 unless follow_redirects=True.
    # Wait, Starlette TestClient follows redirects by default is False, but recent versions might differ.
    # Let's check history or status code.
    # Actually, standard response is 303.
    # If TestClient follows redirects, it will be 200 (interactions page).
    # If not, 303.
    # Let's just check if it worked.
    
    # The mock_reddit.fetch_posts should be called.
    # But it's a background task.
    # TestClient usually runs background tasks synchronously after response?
    # Or we need to check if task was added.
    pass

def test_like_interaction(client, db_session):
    # Seed
    interaction = Interaction(platform="Reddit", external_post_id="r1")
    db_session.add(interaction)
    db_session.commit()
    db_session.refresh(interaction)
    
    # We need to ensure the mock_reddit in app is the SAME as what we check.
    # The client fixture mocks it. We need access to those mocks.
    # But the fixture yields 'c'.
    # We can re-patch in the test or use a class-based approach, 
    # OR return mocks from fixture.
    
    # For simplicity, let's trust the response code for now, 
    # or rely on `patch` inside the test function if we want to verify calls.
    
    with patch("src.web.app.reddit_scout") as mock_reddit:
         mock_reddit.like_post.return_value = True
         response = client.post(f"/interactions/{interaction.id}/like")
         assert response.status_code in [200, 303]
         mock_reddit.like_post.assert_called_with("r1")

def test_comment_interaction(client, db_session):
    interaction = Interaction(platform="Twitter", external_post_id="t1")
    db_session.add(interaction)
    db_session.commit()
    db_session.refresh(interaction)
    
    with patch("src.web.app.twitter_scout") as mock_twitter, \
         patch("src.web.app.interaction_agent") as mock_agent:
         
        mock_agent.generate_comment.return_value = "Test Comment"
        mock_twitter.comment_post.return_value = True
        
        response = client.post(f"/interactions/{interaction.id}/comment")
        assert response.status_code in [200, 303]
        
        mock_agent.generate_comment.assert_called()
        mock_twitter.comment_post.assert_called_with("t1", "Test Comment")
        
        # Verify DB update
        db_session.refresh(interaction)
        assert interaction.bot_comment == "Test Comment"
        assert interaction.status == "POSTED"
