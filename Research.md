# Vibe Coding Engagement Agent: 1-Hour MVP Build Guide

Automated social media engagement for "build in public" communities requires **$200/month minimum for Twitter** (Basic tier), free Reddit API access, and careful attention to platform rules to avoid bans. This guide provides production-ready code for a working MVP that finds relevant posts, generates contextual comments, and maintains idempotency.

## Architecture at a glance

The system uses a simple polling architecture with SQLite persistence. Every 5 minutes, the agent searches both platforms for relevant posts, filters them semantically, generates context-aware comments using an LLM, and posts replies while tracking everything in the database to prevent duplicates.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MAIN AGENT LOOP                              │
│  ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────────────┐│
│  │ Search  │───▶│ Semantic │───▶│   LLM   │───▶│ Post + Store DB  ││
│  │ APIs    │    │ Filter   │    │ Comment │    │ (Idempotent)     ││
│  └─────────┘    └──────────┘    └─────────┘    └──────────────────┘│
│       │              │                                │             │
│       ▼              ▼                                ▼             │
│  ┌─────────┐    ┌──────────┐                   ┌──────────────────┐│
│  │ Twitter │    │ Sentence │                   │    SQLite DB     ││
│  │ Reddit  │    │Transform │                   │  (seen_posts,    ││
│  └─────────┘    └──────────┘                   │   comments)      ││
└─────────────────────────────────────────────────────────────────────┘
```

## Project structure for 1-hour build

```
vibe_agent/
├── main.py              # Entry point and agent loop
├── config.py            # Environment variables
├── db.py                # SQLite operations
├── twitter_client.py    # X/Twitter API wrapper
├── reddit_client.py     # Reddit PRAW wrapper
├── semantic_filter.py   # Embedding-based relevance scoring
├── comment_generator.py # LLM prompt templates
├── requirements.txt
└── tests/
    └── test_db.py
```

**requirements.txt:**
```
tweepy>=4.14.0
praw>=7.7.0
anthropic>=0.34.0
sentence-transformers>=2.2.0
python-dotenv>=1.0.0
pytest>=7.0.0
```

---

## Twitter/X API integration

Twitter's API requires **Basic tier ($200/month)** for search functionality—the free tier is write-only and cannot find tweets to reply to. You'll need OAuth credentials for posting replies.

### Authentication setup

Create a developer app at developer.twitter.com, enable "Read and Write" permissions under User Authentication Settings, then regenerate your access tokens (critical step many miss).

**config.py:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

### Twitter client with search and reply

**twitter_client.py:**
```python
import tweepy
import time
from typing import Optional, List, Dict
import config

class TwitterClient:
    def __init__(self):
        # Read client (search) uses bearer token
        self.read_client = tweepy.Client(bearer_token=config.TWITTER_BEARER_TOKEN)
        
        # Write client (replies) uses OAuth 1.0a
        self.write_client = tweepy.Client(
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET
        )
    
    def search_vibe_coding_tweets(self, max_results: int = 50) -> List[Dict]:
        """Search for relevant tweets from the last 7 days."""
        # Combine keywords with operators - exclude retweets and replies
        query = (
            '("vibe coding" OR "vibe coded" OR "build in public" OR '
            '"shipped" OR "just launched" OR "side project" OR '
            '"weekend project" OR #buildinpublic) '
            '-is:retweet -is:reply lang:en'
        )
        
        try:
            tweets = self.read_client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['id', 'text', 'author_id', 'created_at', 'conversation_id'],
                user_fields=['username', 'name'],
                expansions=['author_id']
            )
            
            if not tweets.data:
                return []
            
            # Build user lookup
            users = {u.id: u for u in (tweets.includes.get('users') or [])}
            
            results = []
            for tweet in tweets.data:
                author = users.get(tweet.author_id)
                results.append({
                    'id': str(tweet.id),
                    'platform': 'twitter',
                    'content': tweet.text,
                    'author': author.username if author else 'unknown',
                    'author_id': str(tweet.author_id),
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None
                })
            
            return results
            
        except tweepy.errors.TooManyRequests:
            print("Twitter rate limit hit. Waiting 15 minutes...")
            time.sleep(900)
            return []
        except tweepy.errors.Forbidden as e:
            print(f"Twitter Forbidden error (check API tier): {e}")
            return []
    
    def post_reply(self, tweet_id: str, message: str) -> Optional[str]:
        """Post a reply to a tweet. Returns new tweet ID or None on failure."""
        try:
            response = self.write_client.create_tweet(
                text=message,
                in_reply_to_tweet_id=tweet_id
            )
            return str(response.data['id'])
        except tweepy.errors.TooManyRequests:
            print("Rate limited on posting. Waiting...")
            time.sleep(900)
            return None
        except tweepy.errors.Forbidden as e:
            print(f"Cannot reply (possibly protected/blocked): {e}")
            return None
        except Exception as e:
            print(f"Twitter post error: {e}")
            return None
```

### Twitter rate limits to remember

| Endpoint | Limit (15 min) | Monthly (Basic) |
|----------|----------------|-----------------|
| Search Recent | 180 requests | ~15,000 tweets read |
| Create Tweet | 200 tweets | 50,000 tweets |
| Tweet Lookup | 900 requests | — |

---

## Reddit API integration with PRAW

Reddit's API is free but requires careful rate limiting and **genuine engagement** to avoid bans. Create an app at reddit.com/prefs/apps (select "script" type).

**reddit_client.py:**
```python
import praw
import prawcore
import time
import random
from typing import List, Dict, Optional
import config

class RedditClient:
    TARGET_SUBREDDITS = [
        "SideProject", "buildinpublic", "startups", 
        "webdev", "IndieHackers", "SaaS", "indiebiz"
    ]
    
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent="VibeCodingBot/1.0 (by u/" + config.REDDIT_USERNAME + ")",
            username=config.REDDIT_USERNAME,
            password=config.REDDIT_PASSWORD
        )
        self._verify_auth()
    
    def _verify_auth(self):
        """Verify we're authenticated properly."""
        try:
            me = self.reddit.user.me()
            print(f"Reddit authenticated as: u/{me.name}")
        except Exception as e:
            raise RuntimeError(f"Reddit auth failed: {e}")
    
    def search_vibe_coding_posts(self, limit_per_sub: int = 20) -> List[Dict]:
        """Search target subreddits for relevant posts."""
        keywords = [
            "launched", "feedback", "mvp", "shipped", 
            "side project", "built this", "weekend project"
        ]
        
        found_posts = []
        
        for sub_name in self.TARGET_SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                
                # Get recent posts (faster than search)
                for submission in subreddit.new(limit=limit_per_sub):
                    # Basic keyword check
                    text = f"{submission.title} {submission.selftext}".lower()
                    if any(kw in text for kw in keywords):
                        found_posts.append({
                            'id': submission.id,
                            'platform': 'reddit',
                            'subreddit': sub_name,
                            'content': f"{submission.title}\n\n{submission.selftext[:500]}",
                            'author': str(submission.author) if submission.author else '[deleted]',
                            'author_id': str(submission.author) if submission.author else None,
                            'url': submission.url,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'created_at': submission.created_utc
                        })
                
                time.sleep(1)  # Be nice to the API
                
            except prawcore.exceptions.Forbidden:
                print(f"Cannot access r/{sub_name} (private/banned)")
            except Exception as e:
                print(f"Error searching r/{sub_name}: {e}")
        
        return found_posts
    
    def post_comment(self, post_id: str, message: str) -> Optional[str]:
        """Post a comment on a submission. Returns comment ID or None."""
        try:
            submission = self.reddit.submission(id=post_id)
            
            # Check if we already commented
            submission.comments.replace_more(limit=0)
            my_username = self.reddit.user.me().name
            for comment in submission.comments.list():
                if comment.author and comment.author.name == my_username:
                    print(f"Already commented on {post_id}")
                    return None
            
            # Check if post is locked
            if submission.locked:
                print(f"Post {post_id} is locked")
                return None
            
            comment = submission.reply(message)
            return comment.id
            
        except prawcore.exceptions.Forbidden:
            print(f"Cannot comment on {post_id} (locked/banned)")
            return None
        except praw.exceptions.RedditAPIException as e:
            for error in e.items:
                if error.error_type == "RATELIMIT":
                    # Parse wait time from message
                    wait_match = re.search(r'(\d+) (minute|second)', error.message)
                    if wait_match:
                        wait_time = int(wait_match.group(1))
                        if 'minute' in error.message:
                            wait_time *= 60
                        print(f"Rate limited. Waiting {wait_time}s")
                        time.sleep(wait_time)
            return None
        except Exception as e:
            print(f"Reddit comment error: {e}")
            return None
```

### Reddit anti-ban best practices

- **Space comments 5-10 minutes apart** minimum
- Use an **aged account with karma** (30+ days, 100+ karma)
- Follow the **9:1 rule**: 9 helpful comments for every 1 promotional
- **Vary your comment text** significantly each time
- Read subreddit rules before engaging

---

## SQLite database with idempotency

The database prevents duplicate comments through UNIQUE constraints and operation tracking.

**db.py:**
```python
import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, Dict, List

DATABASE_PATH = "engagement_bot.db"

@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize all tables."""
    with get_connection() as conn:
        conn.executescript('''
            -- Track all posts we've seen
            CREATE TABLE IF NOT EXISTS seen_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                content TEXT,
                author TEXT,
                relevance_score REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(post_id, platform)
            );
            
            -- Track comments we've made
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                external_comment_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                idempotency_key TEXT UNIQUE
            );
            
            -- Idempotency tracking with TTL
            CREATE TABLE IF NOT EXISTS processed_operations (
                operation_key TEXT PRIMARY KEY,
                operation_type TEXT NOT NULL,
                result_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            );
            
            CREATE INDEX IF NOT EXISTS idx_posts_platform 
                ON seen_posts(platform, created_at);
            CREATE INDEX IF NOT EXISTS idx_comments_status 
                ON comments(status);
        ''')

# --- Post Operations ---
def is_post_seen(post_id: str, platform: str) -> bool:
    """Check if we've already seen this post."""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM seen_posts WHERE post_id = ? AND platform = ?",
            (post_id, platform)
        )
        return cursor.fetchone() is not None

def save_post(post_id: str, platform: str, content: str = None, 
              author: str = None, relevance_score: float = 0.0) -> bool:
    """Save a post. Returns True if new, False if duplicate."""
    with get_connection() as conn:
        try:
            conn.execute(
                """INSERT OR IGNORE INTO seen_posts 
                   (post_id, platform, content, author, relevance_score) 
                   VALUES (?, ?, ?, ?, ?)""",
                (post_id, platform, content, author, relevance_score)
            )
            return conn.total_changes > 0
        except sqlite3.IntegrityError:
            return False

def has_commented(post_id: str, platform: str) -> bool:
    """Check if we've already commented on this post."""
    with get_connection() as conn:
        cursor = conn.execute(
            """SELECT 1 FROM comments 
               WHERE post_id = ? AND platform = ? AND status = 'success'""",
            (post_id, platform)
        )
        return cursor.fetchone() is not None

def save_comment(post_id: str, platform: str, comment_text: str,
                 external_id: str = None, status: str = 'success') -> int:
    """Save a comment record. Returns comment ID."""
    idempotency_key = hashlib.sha256(
        f"{post_id}:{platform}:{datetime.utcnow().date()}".encode()
    ).hexdigest()[:32]
    
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT OR IGNORE INTO comments 
               (post_id, platform, comment_text, external_comment_id, status, idempotency_key) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (post_id, platform, comment_text, external_id, status, idempotency_key)
        )
        return cursor.lastrowid

def get_engagement_history(platform: str, author: str, limit: int = 5) -> List[Dict]:
    """Get previous interactions with an author for context."""
    with get_connection() as conn:
        cursor = conn.execute(
            """SELECT sp.content, c.comment_text, c.created_at
               FROM comments c
               JOIN seen_posts sp ON c.post_id = sp.post_id AND c.platform = sp.platform
               WHERE sp.platform = ? AND sp.author = ?
               ORDER BY c.created_at DESC LIMIT ?""",
            (platform, author, limit)
        )
        return [dict(row) for row in cursor.fetchall()]

def cleanup_old_operations(days: int = 7):
    """Remove old operation records."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM processed_operations WHERE expires_at < CURRENT_TIMESTAMP"
        )
```

---

## Semantic filtering with embeddings

Use sentence-transformers to score post relevance. Posts above the threshold get engagement; others are skipped.

**semantic_filter.py:**
```python
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
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = threshold
        # Pre-compute reference embeddings
        self.reference_embeddings = self.model.encode(
            self.VIBE_CODING_EXAMPLES, 
            convert_to_tensor=True
        )
    
    def score_relevance(self, text: str) -> float:
        """Score how relevant a post is to vibe coding (0.0 to 1.0)."""
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
            score = self.score_relevance(post.get('content', ''))
            post['relevance_score'] = score
            if score >= self.threshold:
                relevant.append(post)
        
        # Sort by relevance, highest first
        return sorted(relevant, key=lambda x: x['relevance_score'], reverse=True)

# Quick keyword-based pre-filter (faster, use before semantic)
def keyword_prefilter(posts: List[Dict]) -> List[Dict]:
    """Fast keyword filter before expensive semantic scoring."""
    MUST_HAVE = [
        'launch', 'ship', 'built', 'building', 'mvp', 'project',
        'feedback', 'vibe', 'indie', 'saas', 'deploy', 'release'
    ]
    SKIP_WORDS = [
        'hiring', 'job', 'salary', 'interview', 'tutorial',
        'course', 'learn', 'beginner', 'question'
    ]
    
    filtered = []
    for post in posts:
        text = post.get('content', '').lower()
        has_keyword = any(kw in text for kw in MUST_HAVE)
        has_skip = any(sw in text for sw in SKIP_WORDS)
        
        if has_keyword and not has_skip:
            filtered.append(post)
    
    return filtered
```

---

## LLM comment generation with Claude

Generate contextual, human-like comments that add genuine value.

**comment_generator.py:**
```python
import anthropic
from typing import Dict, List, Optional
import config
import db
import random

class CommentGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def generate_comment(self, post: Dict, platform: str) -> str:
        """Generate a contextual comment for a post."""
        # Get previous interactions with this author
        history = db.get_engagement_history(platform, post.get('author', ''))
        
        history_context = ""
        if history:
            history_context = f"""
You've interacted with this author before:
{chr(10).join([f"- Previous post: {h['content'][:100]}..." for h in history[:3]])}
Reference this history naturally if relevant.
"""
        
        prompt = f"""You are engaging authentically with a "build in public" / indie developer community post.

POST CONTENT:
{post.get('content', '')}

AUTHOR: {post.get('author', 'unknown')}
PLATFORM: {platform}
{history_context}

Generate a SHORT, genuine comment (1-3 sentences max) that:
1. Shows you actually read and understood the post
2. Asks a specific question OR shares a relevant insight
3. Feels like a real developer wrote it (casual but smart)
4. Does NOT sound promotional or automated
5. Does NOT use generic phrases like "Great work!" or "Love this!"

Vary your style. Sometimes be curious, sometimes share experience, sometimes offer a specific suggestion.

Return ONLY the comment text, nothing else."""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    def should_skip_post(self, post: Dict) -> tuple[bool, str]:
        """Determine if we should skip commenting on this post."""
        content = post.get('content', '').lower()
        
        # Skip promotional/job posts
        skip_patterns = [
            ('hiring', 'Job posting'),
            ('we are looking for', 'Job posting'),
            ('salary', 'Job posting'),
            ('discount', 'Promotional'),
            ('coupon', 'Promotional'),
            ('% off', 'Promotional'),
            ('giveaway', 'Promotional'),
        ]
        
        for pattern, reason in skip_patterns:
            if pattern in content:
                return True, reason
        
        # Skip very short posts
        if len(content) < 50:
            return True, "Post too short"
        
        # Skip posts asking for upvotes/engagement
        if 'upvote' in content or 'please share' in content:
            return True, "Engagement bait"
        
        return False, ""
```

---

## Main agent loop with safety controls

**main.py:**
```python
import time
import signal
import sys
import random
from datetime import datetime

import db
from twitter_client import TwitterClient
from reddit_client import RedditClient
from semantic_filter import SemanticFilter, keyword_prefilter
from comment_generator import CommentGenerator

# Graceful shutdown
running = True
def signal_handler(signum, frame):
    global running
    print("\nShutdown signal received. Finishing current operation...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class VibeCodingAgent:
    def __init__(self):
        print("Initializing Vibe Coding Agent...")
        db.init_database()
        
        self.twitter = TwitterClient()
        self.reddit = RedditClient()
        self.semantic_filter = SemanticFilter(threshold=0.35)
        self.comment_generator = CommentGenerator()
        
        # Safety settings
        self.max_comments_per_run = 3
        self.min_delay_between_comments = 300  # 5 minutes
        self.poll_interval = 600  # 10 minutes
    
    def process_platform(self, platform: str, posts: list) -> int:
        """Process posts from a platform. Returns count of comments made."""
        comments_made = 0
        
        # Pre-filter with keywords
        posts = keyword_prefilter(posts)
        print(f"  After keyword filter: {len(posts)} posts")
        
        # Semantic filtering
        posts = self.semantic_filter.filter_posts(posts)
        print(f"  After semantic filter: {len(posts)} relevant posts")
        
        for post in posts:
            if comments_made >= self.max_comments_per_run:
                print(f"  Reached max comments ({self.max_comments_per_run})")
                break
            
            if not running:
                break
            
            post_id = post['id']
            
            # Check if already seen/commented
            if db.is_post_seen(post_id, platform):
                continue
            
            if db.has_commented(post_id, platform):
                continue
            
            # Save post
            db.save_post(
                post_id, platform,
                content=post.get('content'),
                author=post.get('author'),
                relevance_score=post.get('relevance_score', 0.5)
            )
            
            # Check if we should skip
            should_skip, reason = self.comment_generator.should_skip_post(post)
            if should_skip:
                print(f"  Skipping {post_id}: {reason}")
                continue
            
            # Generate comment
            try:
                comment_text = self.comment_generator.generate_comment(post, platform)
                print(f"  Generated: {comment_text[:80]}...")
            except Exception as e:
                print(f"  LLM error: {e}")
                continue
            
            # Post comment
            try:
                if platform == 'twitter':
                    external_id = self.twitter.post_reply(post_id, comment_text)
                else:
                    external_id = self.reddit.post_comment(post_id, comment_text)
                
                if external_id:
                    db.save_comment(post_id, platform, comment_text, external_id, 'success')
                    comments_made += 1
                    print(f"  ✓ Posted comment on {platform}/{post_id}")
                    
                    # Wait between comments
                    wait = self.min_delay_between_comments + random.randint(0, 120)
                    print(f"  Waiting {wait}s before next comment...")
                    time.sleep(wait)
                else:
                    db.save_comment(post_id, platform, comment_text, None, 'failed')
                    
            except Exception as e:
                print(f"  Error posting: {e}")
                db.save_comment(post_id, platform, comment_text, None, 'failed')
        
        return comments_made
    
    def run_once(self):
        """Single run of the agent."""
        print(f"\n{'='*50}")
        print(f"Agent run at {datetime.now().isoformat()}")
        print('='*50)
        
        total_comments = 0
        
        # Process Twitter
        print("\n[Twitter] Searching for vibe coding tweets...")
        try:
            tweets = self.twitter.search_vibe_coding_tweets(max_results=50)
            print(f"  Found {len(tweets)} tweets")
            total_comments += self.process_platform('twitter', tweets)
        except Exception as e:
            print(f"  Twitter error: {e}")
        
        # Process Reddit
        print("\n[Reddit] Searching target subreddits...")
        try:
            posts = self.reddit.search_vibe_coding_posts(limit_per_sub=20)
            print(f"  Found {len(posts)} posts")
            total_comments += self.process_platform('reddit', posts)
        except Exception as e:
            print(f"  Reddit error: {e}")
        
        print(f"\nRun complete. Made {total_comments} comments.")
        return total_comments
    
    def run_loop(self):
        """Continuous agent loop."""
        print("Starting continuous agent loop...")
        
        while running:
            try:
                self.run_once()
                
                # Cleanup old records periodically
                db.cleanup_old_operations()
                
                if running:
                    print(f"Sleeping {self.poll_interval}s until next run...")
                    time.sleep(self.poll_interval)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(60)
        
        print("Agent stopped.")

if __name__ == "__main__":
    agent = VibeCodingAgent()
    
    if "--once" in sys.argv:
        agent.run_once()
    else:
        agent.run_loop()
```

---

## Testing approach for MVP

Focus on database idempotency and the semantic filter—these prevent costly duplicate posts.

**tests/test_db.py:**
```python
import pytest
import tempfile
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db

@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    original = db.DATABASE_PATH
    db.DATABASE_PATH = path
    db.init_database()
    yield path
    db.DATABASE_PATH = original
    os.unlink(path)

def test_save_post_new(temp_db):
    """New posts should save successfully."""
    result = db.save_post('post_123', 'twitter', 'Test content', 'user1')
    assert result is True

def test_save_post_duplicate_rejected(temp_db):
    """Duplicate posts should be rejected."""
    db.save_post('post_123', 'twitter', 'Content 1', 'user1')
    result = db.save_post('post_123', 'twitter', 'Content 2', 'user2')
    assert result is False  # Duplicate rejected

def test_has_commented_false_initially(temp_db):
    """Should return False before commenting."""
    assert db.has_commented('post_999', 'twitter') is False

def test_has_commented_true_after_success(temp_db):
    """Should return True after successful comment."""
    db.save_comment('post_999', 'twitter', 'Great!', 'ext_123', 'success')
    assert db.has_commented('post_999', 'twitter') is True

def test_idempotency_same_day(temp_db):
    """Comments on same post same day should be rejected."""
    id1 = db.save_comment('post_1', 'twitter', 'Comment 1')
    id2 = db.save_comment('post_1', 'twitter', 'Comment 2')  # Same post
    assert id1 > 0
    assert id2 == 0  # Rejected by idempotency key

# Run: pytest tests/test_db.py -v
```

---

## Critical gotchas and rate limit warnings

### Twitter pitfalls

| Issue | Solution |
|-------|----------|
| 403 Forbidden on search | Upgrade to Basic tier ($200/mo) - free tier can't search |
| 403 on posting replies | Enable "Read and Write" permissions, then **regenerate tokens** |
| Search only returns 7 days | Basic tier limitation; Pro ($5k/mo) gets full archive |
| Query max 512 characters | Keep your search query concise |

### Reddit pitfalls

| Issue | Solution |
|-------|----------|
| Shadowban | Check if your posts are visible logged out; vary comment text |
| BotBouncer flag | Space comments 5-10 min apart, don't use templates |
| RATELIMIT error | Parse wait time from error message, sleep accordingly |
| New account limits | Use aged account (30+ days) with karma (100+) |
| Subreddit bans | Read each subreddit's rules; some ban all bots |

### Cost summary for MVP

| Service | Cost | Notes |
|---------|------|-------|
| Twitter Basic | $200/month | Required for search API |
| Reddit API | Free | 100 requests/minute |
| Claude API | ~$0.003/comment | claude-3-5-sonnet |
| Sentence Transformers | Free | Local inference |

### Safety checklist before deploying

- [ ] Test with `--once` flag first before running loop
- [ ] Verify credentials work on both platforms
- [ ] Use aged Reddit account with karma
- [ ] Set conservative rate limits (5+ min between comments)
- [ ] Monitor for shadowbans weekly
- [ ] Add genuine value—don't just promote
- [ ] Read each subreddit's rules
- [ ] Keep comment variation high

This MVP provides a foundation for responsible engagement. The semantic filter ensures you only engage with truly relevant posts, and the idempotency layer prevents embarrassing duplicate comments. Start with conservative settings, monitor results, and adjust the relevance threshold and comment frequency based on engagement quality.