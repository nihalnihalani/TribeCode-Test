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

        prompt = f"""You are a fellow developer scrolling Twitter/X. You are not an AI assistant. You are just a cool dev interested in what others are building.

TARGET POST:
"{target_post.post_content}"

{history_context}

TASK: Write a reply to the TARGET POST.

GUIDELINES:
- Write like a human. No robotic enthusiasm. No "Great post!"
- Be extremely casual. Use lowercase if it fits the vibe.
- If the post mentions a specific tech (Next.js, Python, databases), ask a specific technical question about it.
- If it's a milestone, give a "nice" or "congrats" but follow up with a question.
- Reference similar things you've seen if relevant, but keep it brief.
- MAX 2 sentences. Usually 1 is enough.
- NO hashtags. NO emojis (unless 1 max).
- NO bullet points. NO lists.
- Do not start with "Hey" or "Hi". Just dive in.

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
