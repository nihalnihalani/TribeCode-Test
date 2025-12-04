import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agents.interaction_agent import InteractionAgent
from src.database import Interaction

class TestInteractionAgentContext(unittest.TestCase):
    
    @patch('src.agents.interaction_agent.anthropic.Anthropic')
    def test_prompt_formatting(self, mock_anthropic):
        # Setup Agent
        agent = InteractionAgent()
        agent.client = MagicMock()
        
        # Test Case 1: Full Context
        interaction = Interaction(
            id=1,
            post_content="Building in public!",
            author_name="Alice",
            author_handle="@alice_dev",
            tag="buildinpublic"
        )
        
        agent.generate_comment(interaction, [])
        
        # Extract prompt sent to API
        call_args = agent.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        self.assertIn("Author: Alice (@alice_dev)", prompt)
        self.assertIn("Topic/Tag: buildinpublic", prompt)
        self.assertIn('TARGET POST:\n"Building in public!"', prompt)

        # Test Case 2: Minimal Context
        interaction_minimal = Interaction(
            id=2,
            post_content="Just code.",
            author_name=None,
            author_handle=None,
            tag=None
        )
        
        agent.generate_comment(interaction_minimal, [])
        
        call_args = agent.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        self.assertNotIn("Author:", prompt) # Should be empty string if missing
        self.assertNotIn("Topic/Tag:", prompt)

        # Test Case 3: Handle without @
        interaction_no_at = Interaction(
            id=3,
            post_content="Hello",
            author_name="Bob",
            author_handle="bob_dev", # No @
            tag="hello"
        )
        
        agent.generate_comment(interaction_no_at, [])
        
        call_args = agent.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        self.assertIn("Author: Bob (@bob_dev)", prompt)

if __name__ == '__main__':
    unittest.main()
