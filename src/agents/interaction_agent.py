import os
from typing import List, Optional
import anthropic
from src.database import Interaction

class InteractionAgent:
    def __init__(self):
        self.client = None
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            print("ANTHROPIC_API_KEY not found. InteractionAgent will not generate comments.")

    def generate_comment(self, target_post: Interaction, context_posts: List[Interaction]) -> Optional[str]:
        """
        Generates a comment for the target post using Claude (Anthropic), 
        referencing previous interactions for style/context.
        """
        if not self.client:
            return "Error: AI Agent not configured (missing Anthropic API key)."

        # Prepare context string (last 5 interactions for better style matching)
        history_context = ""
        if context_posts:
            history_context = "MY PAST COMMENTS (match this vibe - casual, lowercase often, direct):\n"
            history_context += "\n".join([
                f"Context Post: {p.post_content[:80]}... -> My Reply: {p.bot_comment}" 
                for p in context_posts[:5] 
                if p.bot_comment
            ])

        prompt = f"""You are a developer scrolling Twitter.

TARGET POST:
"{target_post.post_content}"

{history_context}

TASK: Write a reply.

GUIDELINES:
1. Casual, short, direct. Lowercase is good.
2. NO bullet points. NEVER start the comment with a hyphen (-).
3. No hashtags. Max 1 emoji.
4. If technical, ask a specific question.
5. No "Great post!" generic comments.
6. Max 2 sentences.
7. Don't use quotes around the reply.

Reply text only:"""

        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Error generating comment with Claude: {e}")
            return None

interaction_agent = InteractionAgent()
