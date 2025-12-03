import pytest
from unittest.mock import MagicMock, patch
import src.web.app
from src.agents.semantic_filter import SemanticFilter

def test_semantic_filter_score():
    """Test that relevant text gets high score and irrelevant text gets low score."""
    sf = SemanticFilter()
    
    relevant_text = "I just shipped my MVP for a new SaaS app! #buildinpublic"
    irrelevant_text = "I am hiring a software engineer for $150k."
    
    score_relevant = sf.score_relevance(relevant_text)
    score_irrelevant = sf.score_relevance(irrelevant_text)
    
    print(f"Relevant Score: {score_relevant}")
    print(f"Irrelevant Score: {score_irrelevant}")
    
    assert score_relevant > score_irrelevant
    assert score_relevant > 0.3 # Assuming threshold is around 0.35, decent match should be higher

def test_keyword_prefilter():
    from src.agents.semantic_filter import keyword_prefilter
    
    posts = [
        {"text": "Just launched my project"},
        {"text": "Hiring a developer"},
        {"text": "Random noise"}
    ]
    
    filtered = keyword_prefilter(posts)
    
    assert len(filtered) == 1
    assert filtered[0]["text"] == "Just launched my project"

@patch('src.web.app.twitter_scout.fetch_posts')
@patch('src.web.app.keyword_prefilter')
@patch('src.web.app.semantic_filter.filter_posts')
def test_run_scout_task(mock_semantic, mock_keyword, mock_fetch):
    """Test the scouting orchestration function."""
    # Setup Mocks
    mock_fetch.return_value = [{"text": "raw tweet"}]
    mock_keyword.return_value = [{"text": "keyword filtered"}]
    mock_semantic.return_value = [{"text": "final tweet"}]
    
    # Run
    src.web.app.run_scout_task("twitter", 10, "test query")
    
    # Verify
    mock_fetch.assert_called_with(keywords=["test query"], limit=10)
    mock_keyword.assert_called()
    mock_semantic.assert_called()

