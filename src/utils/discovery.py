from typing import List
import random

class TopicDiscovery:
    def __init__(self):
        self.trending_cache = [
            "AI Agents", "SaaS Marketing", "Micro-SaaS", 
            "Solo Founder", "No-Code Tools", "Open Source",
            "NextJS Boilerplate", "Stripe Integration",
            "LLM Wrapper", "Growth Hacking"
        ]

    def get_suggested_topics(self, limit: int = 5) -> List[str]:
        """
        Returns a list of suggested trending topics for 'Build in Public'.
        In a real app, this would fetch from an API or analyze previous successful hits.
        """
        return random.sample(self.trending_cache, min(limit, len(self.trending_cache)))

    def get_smart_query(self) -> str:
        """Returns a single optimized query string combining multiple trending topics."""
        topics = self.get_suggested_topics(limit=2)
        return " OR ".join([f'"{t}"' for t in topics])

topic_discovery = TopicDiscovery()

