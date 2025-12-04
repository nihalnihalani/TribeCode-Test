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
    
    # Create a dummy interaction
    interaction = Interaction(
        id=1,
        platform="Twitter",
        post_content="Just launched my new SaaS! #buildinpublic",
        bot_comment=None
    )
    
    comment = interaction_agent.generate_comment(interaction, [])
    
    if comment:
        print(f"SUCCESS: Generated comment: {comment}")
    else:
        print("FAILURE: Could not generate comment.")
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("Reason: ANTHROPIC_API_KEY not set in environment.")

if __name__ == "__main__":
    test_generation()
