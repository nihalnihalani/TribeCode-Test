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
        
        # Mock internal methods to avoid actual browser interactions but track calls
        # IMPORTANT: Since engage_post calls self.like_post, we need to mock these ON THE INSTANCE
        # BUT engage_post is bound to the instance. We need to patch them carefully.
        
        # We'll use a wrapper or just trust the mock replacement
        # Create a new method that calls the mock so we can track it, 
        # but since we are replacing the bound method on the instance, 'self' is bound already.
        
        # When engage_post calls self.like_post(tweet_id, page=page), it looks up 'like_post' on self.
        # If we replace it with a mock, it should work.
        
        # The failure suggests that the mock is NOT being called.
        # This might be because the method is being looked up on the class or something else is weird.
        
        # Let's try patching the class methods instead of the instance methods for this test
        # OR simply rely on printing since the previous output showed the print statements working!
        
        # The output showed:
        # [Engage] Step 1: Attempting to Like...
        # [Engage] Step 2: Attempting to Reply...
        
        # This confirms the flow logic works: Like is attempted first (Step 1), then Reply (Step 2).
        
        # To make the test pass with assertions, we can use patch.object on the class temporarily
        # But patching on the instance should work.
        
        # Let's try a different approach:
        # We will not mock like_post/comment_post but instead mock the page interactions they do.
        # engage_post -> like_post -> page.query_selector...
        
        # Actually, let's just assert that the print statements happened in order, or use a side_effect.
        
        # Let's just fix the mock setup.
        with patch.object(scout, 'like_post', wraps=scout.like_post) as mock_like:
            with patch.object(scout, 'comment_post', wraps=scout.comment_post) as mock_comment:
                 # We still want to avoid actual network calls, so we mock the internals of like/comment via page mock
                 # But wait, if we wrap, it calls the real method.
                 # Let's just replace them completely again but ensure we do it right.
                 pass
        
        # Re-attempting simple mock replacement
        scout.like_post = MagicMock(return_value=True)
        scout.comment_post = MagicMock(return_value=True)
        
        # Define vars
        tweet_id = "12345"
        text = "Nice post!"
        
        # The issue: engage_post calls self.like_post(). 
        # But if engage_post was defined when self.like_post pointed to the original method, 
        # replacing it on the instance MIGHT not work if it's cached or something, 
        # but normally in Python it does look up on 'self' at runtime.
        
        # However, the output shows:
        # "Tweet 12345 is already liked."
        
        # This string comes from the ORIGINAL like_post method!
        # Wait, no, it comes from engage_post ITSELF!
        
        # Let's look at src/agents/twitter_scout.py:
        # def engage_post(self, ...):
        #    ...
        #    # 1. Like
        #    if like:
        #        try:
        #            if page.query_selector('button[data-testid="unlike"]'):
        #                 print(f"  [Engage] Tweet {tweet_id} is already liked.")
        #            else:
        #                 like_button = ...
        
        # AHA! The engage_post method has INLINED logic for liking! 
        # It does NOT call self.like_post() inside the try/except block shown in the logs!
        
        # Let's check the code I just updated in twitter_scout.py:
        # It says:
        #             if like:
        #                print("  [Engage] Step 1: Attempting to Like...")
        #                try:
        #                    if page.query_selector('button[data-testid="unlike"]'):
        #                        print(f"  [Engage] Tweet {tweet_id} is already liked.")
        #                    else:
        #                        like_button = page.wait_for_selector('button[data-testid="like"]', timeout=5000)
        #                        if like_button:
        #                            like_button.scroll_into_view_if_needed()
        #                            like_button.click()
        #                            print(f"  [Engage] Clicked Like on {tweet_id}")
        #                            time.sleep(1)
        #                        else:
        #                            print("  [Engage] Like button not found.")
        
        # It DOES NOT call self.like_post()! It implements the logic directly.
        # This explains why mocking like_post didn't work - it's never called.
        
        # However, it DOES call self.comment_post() at the end:
        # return self.comment_post(tweet_id, text, page=page)
        
        # So we should verify:
        # 1. The "Like" logic was executed (via page interactions)
        # 2. comment_post was called
        
        # Setup page mock to simulate "not liked yet" so we see the click
        mock_page.query_selector.return_value = None # unlike button not found
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
