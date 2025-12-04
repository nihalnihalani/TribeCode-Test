import pytest
import os
from unittest.mock import MagicMock, patch
from src.agents.interaction_agent import InteractionAgent
from src.database import Interaction
import src.web.app

@patch('src.agents.interaction_agent.anthropic.Anthropic')
@patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-fake-key"})
def test_generate_comment_anthropic(mock_anthropic):
    """Test that InteractionAgent uses Anthropic client correctly."""
    # Setup Mock
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_response = MagicMock()
    # Mock the nested structure of Anthropic response
    mock_content = MagicMock()
    mock_content.text = "Cool project!"
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response
    
    # Initialize Agent (should see env var now)
    agent = InteractionAgent()
    
    # Create Dummy Interaction
    target = Interaction(post_content="Just shipped my MVP!", platform="Twitter")
    context = [Interaction(post_content="Old post", bot_comment="Nice work")]
    
    # Run
    comment = agent.generate_comment(target, context)
    
    # Verify
    assert comment == "Cool project!"
    mock_client.messages.create.assert_called_once()
    call_args = mock_client.messages.create.call_args[1]
    assert call_args['model'] == "claude-haiku-4-5"
    assert "Just shipped my MVP!" in call_args['messages'][0]['content']

@patch('src.web.app.twitter_scout.fetch_posts')
def test_auto_pilot_multiple_keywords(mock_fetch):
    """Test that query='auto' triggers multiple searches."""
    # Setup Mock
    mock_fetch.return_value = []
    
    # Run logic directly (simulating the task)
    src.web.app.run_scout_task("twitter", 5, "auto")
    
    # Verify multiple calls
    assert mock_fetch.call_count >= 3 # We have 4 keywords in auto list
    
    # Check some calls
    # mock_calls structure is (name, args, kwargs)
    # We want the 'keywords' kwarg from call_args
    
    # Get list of keywords passed in each call
    keywords_searched = []
    for call in mock_fetch.mock_calls:
        # call is tuple: (name, args, kwargs) or just call object
        # call.kwargs should exist
        if 'keywords' in call.kwargs:
            keywords_searched.extend(call.kwargs['keywords'])
            
    assert "build in public" in keywords_searched
    assert "indie hacker" in keywords_searched
