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
        with patch("src.web.app.twitter_scout") as mock_twitter, \
             patch("src.web.app.interaction_agent") as mock_agent:
            
            # Setup common mocks
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
    db_session.add(Interaction(platform="Twitter", external_post_id="t1", post_content="Twitter Post"))
    db_session.commit()
    
    response = client.get("/interactions")
    assert response.status_code == 200
    assert "Twitter Post" in response.text

def test_scout_trigger(client):
    response = client.post("/scout", data={
        "platform": "twitter",
        "limit": 5,
        "query": "test"
    })
    # Redirects to interactions. TestClient usually follows or returns 200/303.
    # With TestClient, it usually follows redirects by default unless specified.
    # Let's verify.
    assert response.status_code == 200
    assert "/interactions" in str(response.url)

def test_like_interaction(client, db_session):
    # Seed
    interaction = Interaction(platform="Twitter", external_post_id="t1")
    db_session.add(interaction)
    db_session.commit()
    db_session.refresh(interaction)
    
    with patch("src.web.app.twitter_scout") as mock_twitter:
         mock_twitter.like_post.return_value = True
         response = client.post(f"/interactions/{interaction.id}/like")
         # Redirects
         assert response.status_code == 200 
         mock_twitter.like_post.assert_called_with("t1")

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
        assert response.status_code == 200
        
        mock_agent.generate_comment.assert_called()
        mock_twitter.comment_post.assert_called_with("t1", "Test Comment")
        
        # Verify DB update
        db_session.expire_all()
        updated = db_session.query(Interaction).filter_by(id=interaction.id).first()
        assert updated.bot_comment == "Test Comment"
        assert updated.status == "POSTED"
