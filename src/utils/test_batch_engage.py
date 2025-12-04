import unittest
from unittest.mock import MagicMock, patch, ANY
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agents.twitter_scout import TwitterScout

class TestTwitterBatchEngage(unittest.TestCase):
    
    @patch('src.agents.twitter_scout.sync_playwright')
    @patch('src.agents.twitter_scout.save_interaction')
    @patch('src.agents.twitter_scout.get_all_interactions')
    def test_batch_engage_integration(self, mock_get_interactions, mock_save_interaction, mock_playwright):
        # Setup Mocks
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_p = mock_playwright.return_value.__enter__.return_value
        mock_p.chromium.launch_persistent_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock finding tweets
        mock_tweet = MagicMock()
        mock_time = MagicMock()
        mock_parent = MagicMock()
        
        # Setup element query chain for ID extraction
        mock_page.query_selector_all.return_value = [mock_tweet]
        
        # FIX: The test failed because it thought there was media (image) and skipped comment generation
        # "Skipping comment on 12345 due to image/media."
        # This is because we mocked query_selector globally for the page, but didn't handle the 'tweetPhoto' check specifically in the batch loop
        # which runs: if page.query_selector('div[data-testid="tweetPhoto"]'): has_media = True
        
        # We need to ensure that when it checks for photo, it returns None
        def page_query_selector_side_effect(selector):
            if selector == 'div[data-testid="tweetPhoto"]':
                return None
            if selector == 'div[data-testid="tweetText"]':
                return MagicMock(inner_text=lambda: "Some text")
            return MagicMock() # Default return for other selectors like article[data-testid="tweet"]
            
        mock_page.query_selector.side_effect = page_query_selector_side_effect
        
        mock_tweet.query_selector.side_effect = lambda s: mock_time if s == 'time' else (MagicMock() if s == 'div[data-testid="tweetText"]' else None)
        mock_time.query_selector.return_value = mock_parent
        mock_parent.get_attribute.return_value = "/user/status/12345"
        
        # Mock Interaction Agent
        mock_agent = MagicMock()
        mock_agent.generate_comment.return_value = "Great post!"
        
        # Mock DB Interaction Object
        mock_interaction = MagicMock()
        mock_interaction.bot_comment = None # Not commented yet
        mock_save_interaction.return_value = mock_interaction
        
        # Initialize Scout
        scout = TwitterScout()
        
        # Mock internal methods to isolate batch logic from actual browser actions
        # We want to verify batch_engage calls engage_post correctly
        scout.ensure_logged_in = MagicMock()
        scout.engage_post = MagicMock(return_value=True)
        
        # Execute
        keywords = ["test"]
        scout.batch_engage(keywords, limit=1, auto_like=True, auto_comment=True, interaction_agent=mock_agent)
        
        # Verify
        # 1. Check if engage_post was called with correct params
        scout.engage_post.assert_called_with("12345", "Great post!", like=True, page=mock_page)
        
        # 2. Check if DB was updated with POSTED status
        # save_interaction is called multiple times. 
        # First for archiving (ARCHIVED), then for updating (POSTED)
        # We check if it was called with status="POSTED"
        calls = mock_save_interaction.call_args_list
        posted_call = any(call.kwargs.get('status') == 'POSTED' for call in calls)
        self.assertTrue(posted_call, "Database should be updated with POSTED status")

    @patch('src.agents.twitter_scout.sync_playwright')
    def test_engage_post_like_only(self, mock_playwright):
        # Setup Mocks
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_p = mock_playwright.return_value.__enter__.return_value
        mock_p.chromium.launch_persistent_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        scout = TwitterScout()
        scout.comment_post = MagicMock()
        
        # Mock Like button finding
        mock_page.query_selector.return_value = None # Not liked yet
        mock_like_btn = MagicMock()
        mock_page.wait_for_selector.return_value = mock_like_btn

        # Execute engage_post with text=None (Like Only)
        scout.engage_post("12345", text=None, like=True, page=mock_page)
        
        # Verify
        # Like button should be clicked
        mock_like_btn.click.assert_called()
        
        # Comment post should NOT be called
        scout.comment_post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
