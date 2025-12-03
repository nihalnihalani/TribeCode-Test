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

        # Prepare context string (last 3 interactions)
        history_context = ""
        if context_posts:
            history_context = "Here are some previous posts/comments for context on tone (do not copy them directly):\n"
            history_context += "\n".join([
                f"- Post: {p.post_content[:100]}... | Comment: {p.bot_comment[:100]}..." 
                for p in context_posts[:3] 
                if p.bot_comment
            ])

        prompt = f"""You are engaging authentically with a "build in public" / indie developer community post.

POST CONTENT:
{target_post.post_content}

PLATFORM: {target_post.platform}

{history_context}

Generate a SHORT, genuine comment (1-3 sentences max) that:
1. Shows you actually read and understood the post.
2. Asks a specific question OR shares a relevant insight.
3. Feels like a real developer wrote it (casual but smart).
4. Does NOT sound promotional or automated.
5. Does NOT use generic phrases like "Great work!" or "Love this!".
6. Uses lowercase sparingly or casual punctuation to fit the vibe if appropriate.

Vary your style. Sometimes be curious, sometimes share experience, sometimes offer a specific suggestion.

Return ONLY the comment text, nothing else."""

        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Error generating comment with Claude: {e}")
            return None

interaction_agent = InteractionAgent()
