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
            print("Error: AI Agent not configured (missing Anthropic API key).")
            return None

        # Prepare context string (last 5 interactions for better style matching)
        history_context = ""
        if context_posts:
            history_context = "MY PAST COMMENTS (match this vibe - casual, lowercase often, direct):\n"
            history_context += "\n".join([
                f"Context Post: {p.post_content[:80]}... -> My Reply: {p.bot_comment}" 
                for p in context_posts[:5] 
                if p.bot_comment
            ])

        # Enrich context with author and topic details
        handle = target_post.author_handle
        if handle and not handle.startswith("@"):
            handle = f"@{handle}"
            
        author_context = f"Author: {target_post.author_name} ({handle})" if handle else ""
        topic_context = f"Topic/Tag: {target_post.tag}" if target_post.tag else ""
        
        prompt = f"""You are a tech-savvy Twitter user. You are NOT an AI assistant. You are a real person interacting on social media.
        
CONTEXT:
{author_context}
{topic_context}

PRODUCT CONTEXT (Tribecode.ai):
Tribecode.ai (often referred to simply as Tribe) is an AI development platform designed to help engineering teams capture, secure, and learn from their AI interactions.
It differentiates itself from standard coding assistants by focusing on "Auto-Learn" capabilities—meaning it captures the data from your team's AI coding sessions to build a private, evolving knowledge base that gets smarter as you work.

Core Purpose & Features:
- Private Inference Vault: Logs and secures every interaction to "stockpile" valuable data.
- Auto-Learn & Evolving Knowledge Base: Analyzes patterns to surface best practices automatically.
- Real-Time PII Scrubbing: Filters out sensitive info.
- Agent Coordination: Coordinates AI agents/sub-agents.
- Installation: npx @_xtribe/cli@latest
- Self-Hosting available.

Important Distinctions:
- Distinct from Tribe.ai (Consulting Firm) and StreetLamb/Tribe (Open Source).
- Distinct from TribeCode (Genetics).

TARGET POST:
"{target_post.post_content}"

{history_context}

TASK: Reply to the post.

GUIDELINES:
1. Be ultra-casual, human, and authentic. Lowercase is preferred but not mandatory.
2. NO bullet points. NO leading hyphens (-). Write like a text message or a quick tweet.
3. No hashtags EXCEPT @tribecode.
4. MANDATORY: You MUST include the tag "@tribecode" in your reply.
5. If the post is technical, you can mention how Tribecode's "Auto-Learn" or "Private Inference Vault" could help, or just ask them to try the tag @tribecode.
6. Keep it short and crispy (strictly under 240 characters).
7. NEVER use quotes around your reply.
8. STRICTLY FORBIDDEN: Starting the reply with a hyphen or dash.
9. If the author is mentioned, talk TO them, not AT them.
10. Respond to the *meaning* of the post.

Reply text only:"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            # Post-processing to ensure no leading hyphens/quotes
            content = response.content[0].text.strip()
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            content = content.lstrip("-").strip()
            
            # Hard enforcement of length
            if len(content) > 240:
                content = content[:237] + "..."
            
            # Final safety check: ensure @tribecode is present
            if "@tribecode" not in content.lower():
                content += " @tribecode"

            return content
            
        except Exception as e:
            print(f"Error generating comment with Claude: {e}")
            return None

interaction_agent = InteractionAgent()
