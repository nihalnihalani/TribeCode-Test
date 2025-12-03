from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict

class SemanticFilter:
    # Reference sentences that define "vibe coding" content
    VIBE_CODING_EXAMPLES = [
        "Just shipped my side project after 2 weeks of vibe coding",
        "Building in public: launched my MVP today",
        "Weekend project turned into something real",
        "Finally launched the thing I've been working on",
        "Shipped a new feature for my indie project",
        "Just launched my SaaS MVP, looking for feedback",
        "Been building this side project, finally deployed it",
        "Vibe coded a tool to solve my own problem"
    ]
    
    def __init__(self, threshold: float = 0.35):
        # Using a smaller model for efficiency, as per research
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = threshold
        # Pre-compute reference embeddings
        self.reference_embeddings = self.model.encode(
            self.VIBE_CODING_EXAMPLES, 
            convert_to_tensor=True
        )
    
    def score_relevance(self, text: str) -> float:
        """Score how relevant a post is to vibe coding (0.0 to 1.0)."""
        if not text or len(text.strip()) < 10:
            return 0.0
            
        text_embedding = self.model.encode([text], convert_to_tensor=True)
        
        # Calculate similarity to all reference examples
        similarities = self.model.similarity(
            text_embedding, 
            self.reference_embeddings
        )[0]
        
        # Return max similarity as the relevance score
        return float(similarities.max())
    
    def filter_posts(self, posts: List[Dict]) -> List[Dict]:
        """Filter posts to only those above relevance threshold."""
        relevant = []
        for post in posts:
            content = post.get('post_content') or post.get('content') or post.get('text') or ""
            score = self.score_relevance(content)
            # We can inject the score back into the dict if needed, 
            # but for now we just filter
            if score >= self.threshold:
                relevant.append(post)
        
        return relevant

# Quick keyword-based pre-filter (faster, use before semantic)
def keyword_prefilter(posts: List[Dict]) -> List[Dict]:
    """Fast keyword filter before expensive semantic scoring."""
    MUST_HAVE = [
        'launch', 'ship', 'built', 'building', 'mvp', 'project',
        'feedback', 'vibe', 'indie', 'saas', 'deploy', 'release',
        'build in public', 'side project', 'startup', 'coding'
    ]
    SKIP_WORDS = [
        'hiring', 'job', 'salary', 'interview', 'tutorial',
        'course', 'learn', 'beginner', 'question'
    ]
    
    filtered = []
    for post in posts:
        text = (post.get('post_content') or post.get('content') or post.get('text') or "").lower()
        has_keyword = any(kw in text for kw in MUST_HAVE)
        has_skip = any(sw in text for sw in SKIP_WORDS)
        
        if has_keyword and not has_skip:
            filtered.append(post)
    
    return filtered

semantic_filter = SemanticFilter()

