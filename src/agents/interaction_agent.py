import os
from typing import List, Optional
from openai import OpenAI
from src.database import Interaction, get_all_interactions

class InteractionAgent:
    def __init__(self):
        self.client = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            print("OPENAI_API_KEY not found. InteractionAgent will not generate comments.")

    def generate_comment(self, target_post: Interaction, context_posts: List[Interaction]) -> Optional[str]:
        """
        Generates a comment for the target post, using other posts as context/style reference.
        """
        if not self.client:
            return "Error: AI Agent not configured (missing API key)."

        # Prepare context string
        context_str = "\n\n".join([
            f"Post [{p.platform}]: {p.post_content[:200]}..." 
            for p in context_posts 
            if p.id != target_post.id
        ])

        prompt = f"""
You are a helpful and engaging social media bot. 
Your goal is to write a relevant, friendly, and constructive comment for the following post.

TARGET POST ({target_post.platform}):
{target_post.post_content}

CONTEXT (Recent posts we've seen, to understand the vibe):
{context_str}

INSTRUCTIONS:
1. Keep the comment under 280 characters.
2. Be encouraging and specific to the post content.
3. Do not sound robotic.
4. If the post is a question, try to answer or point to a resource.
5. Based on the context, try to maintain a consistent persona (helpful indie hacker).

COMMENT:
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for social media interactions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating comment: {e}")
            return None

interaction_agent = InteractionAgent()

