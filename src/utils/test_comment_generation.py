import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agents.interaction_agent import interaction_agent
from src.database import Interaction

def test_generation():
    print("Testing Interaction Agent Comment Generation...")
    
    # Create a dummy interaction with more context
    interaction = Interaction(
        id=1,
        platform="Twitter",
        post_content="Just launched my new SaaS! It helps developers manage their environment variables easier. #buildinpublic #devtools",
        author_name="Alex Dev",
        author_handle="alexcodez",
        tag="devtools",
        bot_comment=None
    )
    
    # Create some dummy context posts
    context_post = Interaction(
        id=2,
        platform="Twitter",
        post_content="Python 3.12 is looking great.",
        bot_comment="yeah the error messages are finally readable lol"
    )
    
    print(f"Target Post: {interaction.post_content}")
    print(f"Author: {interaction.author_name} (@{interaction.author_handle})")
    
    comment = interaction_agent.generate_comment(interaction, [context_post])
    
    if comment:
        print(f"\nSUCCESS: Generated comment:\n{comment}")
    else:
        print("\nFAILURE: Could not generate comment.")
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("Reason: ANTHROPIC_API_KEY not set in environment.")

if __name__ == "__main__":
    test_generation()
