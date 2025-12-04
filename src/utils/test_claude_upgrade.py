import os
import unittest
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, os.getcwd())
from src.agents.interaction_agent import InteractionAgent, Interaction

class TestClaudeUpgrade(unittest.TestCase):
    
    @patch('src.agents.interaction_agent.anthropic.Anthropic')
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"})
    def test_model_version(self, mock_anthropic):
        # Setup Mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test comment")]
        mock_client.messages.create.return_value = mock_response
        
        # Init Agent
        agent = InteractionAgent()
        
        # Mock Interaction
        target = Interaction(post_content="Test post", platform="Twitter")
        context = []
        
        # Call generate
        agent.generate_comment(target, context)
        
        # Verify Model ID
        call_args = mock_client.messages.create.call_args[1]
        print(f"Called with model: {call_args['model']}")
        self.assertEqual(call_args['model'], "claude-3-5-haiku-20241022")

if __name__ == '__main__':
    unittest.main()

