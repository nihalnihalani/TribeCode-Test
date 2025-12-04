import sys
from pathlib import Path
# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import unittest
from unittest.mock import MagicMock, patch
from src.agents.twitter_scout import TwitterScout

class TestTwitterEngageFlow(unittest.TestCase):

    @patch('src.agents.twitter_scout.sync_playwright')
    def test_engage_post_sequence(self, mock_playwright):
        # Setup mock
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        # Configure playwright mock chain
        mock_p = mock_playwright.return_value.__enter__.return_value
        mock_p.chromium.launch_persistent_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Initialize Scout
        scout = TwitterScout()
        scout.comment_post = MagicMock(return_value=True)
        
        tweet_id = "12345"
        text = "Nice post!"

        # Setup page mock to simulate "not liked yet" so we see the click
        # Need strict side effects to simulate "unlike" button not found, but "like" button found
        def page_query_side_effect(selector):
            if 'unlike' in selector:
                return None
            return MagicMock()
            
        mock_page.query_selector.side_effect = page_query_side_effect
        
        mock_like_btn = MagicMock()
        mock_page.wait_for_selector.return_value = mock_like_btn # like button found
        
        # Execute
        scout.engage_post(tweet_id, text, like=True, page=mock_page)
        
        # Verify Like Logic (Click)
        mock_like_btn.click.assert_called()
        print("Like button click verified.")
        
        # Verify Comment Call
        scout.comment_post.assert_called_with("12345", "Nice post!", page=mock_page)
        print("comment_post call verified.")
        
        print("Test Passed: engage_post executes Like logic then calls comment_post")
        
if __name__ == '__main__':
    unittest.main()
