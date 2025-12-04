import sys
import unittest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agents.interaction_agent import InteractionAgent
from src.agents.twitter_scout import TwitterScout
from src.database import Interaction

class TestExtensiveSuite(unittest.TestCase):

    def setUp(self):
        # Mocks
        self.mock_page = MagicMock()
        self.mock_context = MagicMock()
        self.mock_context.new_page.return_value = self.mock_page
        self.mock_browser = MagicMock()
        
        # Interaction Agent Mock
        self.agent = InteractionAgent()
        self.agent.client = MagicMock() # Mock Anthropic client
        
        # Twitter Scout Instance (patched playwright later)
        self.scout = TwitterScout()

    # --- Interaction Agent Tests ---

    def test_interaction_agent_context(self):
        """Verify InteractionAgent uses author/tag context in prompt."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Human reply")]
        self.agent.client.messages.create.return_value = mock_response
        
        interaction = Interaction(
            external_post_id="123",
            post_content="Hello world",
            author_name="Alice",
            author_handle="@alice",
            tag="coding"
        )
        
        self.agent.generate_comment(interaction, [])
        
        # Check if prompt contains context
        call_args = self.agent.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        self.assertIn("Author: Alice (@alice)", prompt)
        self.assertIn("Topic/Tag: coding", prompt)
        print("[Pass] InteractionAgent prompt contains author and tag context.")

    def test_interaction_agent_missing_context(self):
        """Verify InteractionAgent handles missing context gracefully."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Simple reply")]
        self.agent.client.messages.create.return_value = mock_response
        
        interaction = Interaction(
            external_post_id="456",
            post_content="Just content"
            # Missing author/tag
        )
        
        self.agent.generate_comment(interaction, [])
        
        call_args = self.agent.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        # Should not fail, just omit
        # Since logic is: f"Author: {p.author_name}..." if p.author_handle else ""
        # author_handle is None, so empty string
        self.assertNotIn("Author:", prompt) 
        print("[Pass] InteractionAgent handles missing context.")

    # --- Twitter Scout Extensive Tests ---

    @patch('src.agents.twitter_scout.sync_playwright')
    def test_engage_post_already_liked(self, mock_playwright):
        """Test engage_post when tweet is already liked."""
        # Setup mocks
        mock_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context.return_value = self.mock_context
        
        # Mock Page State: Unlike button exists -> Already Liked
        self.mock_page.query_selector.side_effect = lambda s: MagicMock() if 'unlike' in s else None
        
        self.scout.comment_post = MagicMock(return_value=True) # Mock comment part
        
        self.scout.engage_post("123", "Reply", like=True, page=self.mock_page)
        
        # Verify
        # Should NOT click like (since unlike exists)
        # Should call comment
        self.scout.comment_post.assert_called_once()
        print("[Pass] engage_post respects 'already liked' state.")

    @patch('src.agents.twitter_scout.sync_playwright')
    def test_engage_post_like_fails_comment_succeeds(self, mock_playwright):
        """Test flow continues if Like fails."""
        mock_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context.return_value = self.mock_context
        
        # Mock: Like button found, but click raises error
        like_btn = MagicMock()
        like_btn.click.side_effect = Exception("Click blocked")
        self.mock_page.wait_for_selector.return_value = like_btn
        self.mock_page.query_selector.return_value = None # Not liked yet
        
        self.scout.comment_post = MagicMock(return_value=True)
        
        self.scout.engage_post("123", "Reply", like=True, page=self.mock_page)
        
        # Should attempt like (fail caught) -> then comment
        like_btn.click.assert_called_once()
        self.scout.comment_post.assert_called_once()
        print("[Pass] engage_post proceeds to comment even if like fails.")

    @patch('src.agents.twitter_scout.sync_playwright')
    def test_engage_post_skip_comment(self, mock_playwright):
        """Test engage_post with text=None skips comment."""
        mock_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context.return_value = self.mock_context
        
        # Mock: Not liked, like succeeds
        self.mock_page.query_selector.return_value = None
        like_btn = MagicMock()
        self.mock_page.wait_for_selector.return_value = like_btn
        
        self.scout.comment_post = MagicMock()
        
        self.scout.engage_post("123", text=None, like=True, page=self.mock_page)
        
        like_btn.click.assert_called()
        self.scout.comment_post.assert_not_called()
        print("[Pass] engage_post skips comment when text is None.")

    @patch('src.agents.twitter_scout.sync_playwright')
    @patch('src.agents.twitter_scout.save_interaction')
    @patch('src.agents.twitter_scout.get_all_interactions')
    def test_batch_engage_integration(self, mock_get_interactions, mock_save, mock_playwright):
        """Verify batch_engage uses engage_post correctly."""
        mock_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context.return_value = self.mock_context
        
        # Mock Search Results
        # We need to mock query_selector_all to return a list of tweets
        # Then inside the loop, it calls engage_post
        
        # Mock Tweets
        tweet_el = MagicMock()
        tweet_el.query_selector.return_value = MagicMock() # time element
        # Need to mock href parsing logic...
        # ... href='/user/status/123'
        
        # This is getting complex to mock the DOM parsing fully.
        # Instead, let's just mock `scout.engage_post` and run `batch_engage` 
        # assuming the parsing works (or mock the internal list if possible, but it's local var).
        
        # We'll just verify the call inside the loop by mocking engage_post on the instance
        self.scout.engage_post = MagicMock(return_value=True)
        self.scout.ensure_logged_in = MagicMock()
        self.scout.login = MagicMock()
        
        # Setup minimal DOM mock to enter the loop
        # mock page.query_selector_all returns [tweet_el]
        # tweet_el... href extraction
        time_el = MagicMock()
        link_el = MagicMock()
        link_el.get_attribute.return_value = "/user/status/123"
        time_el.query_selector.return_value = link_el
        tweet_el.query_selector.side_effect = lambda s: time_el if 'time' in s else None
        
        self.mock_page.query_selector_all.return_value = [tweet_el]
        
        # IMPORTANT: Fix query_selector to return None by default (e.g. for tweetPhoto)
        # Otherwise MagicMock() is truthy -> has_media = True -> auto_comment = False
        self.mock_page.query_selector.return_value = None 
        
        # Interaction Agent Mock
        mock_agent = MagicMock()
        mock_agent.generate_comment.return_value = "Generated Reply"
        
        # DB Mock
        mock_interaction = MagicMock()
        mock_interaction.bot_comment = None
        mock_save.return_value = mock_interaction
        
        # Execute
        self.scout.batch_engage(["test"], 1, auto_like=True, auto_comment=True, interaction_agent=mock_agent)
        
        # Verify engage_post called with correct args
        self.scout.engage_post.assert_called_with("123", "Generated Reply", like=True, page=self.mock_page)
        print("[Pass] batch_engage calls engage_post with generated comment.")

if __name__ == '__main__':
    unittest.main()
