import os
import praw
from typing import List, Dict
from dotenv import load_dotenv
from src.database import save_interaction, check_deduplication

load_dotenv()

class RedditScout:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD")
        )
        self.validate_auth()

    def validate_auth(self):
        """Checks if credentials are valid by accessing the user."""
        try:
            # Only check if credentials are provided to avoid error on init during testing if env not set
            if os.getenv("REDDIT_CLIENT_ID"):
                print(f"Authenticated as: {self.reddit.user.me()}")
            else:
                print("Reddit credentials not found in env. Running in limited/mock mode.")
        except Exception as e:
            print(f"Reddit Auth Error: {e}")

    def fetch_posts(self, subreddits: List[str], search_query: str = "build in public", limit: int = 10) -> List[Dict]:
        """
        Searches for posts in the given subreddits matching the query.
        Archives them to the DB immediately.
        """
        found_posts = []
        
        # Combine subreddits into a single string like "SaaS+startups"
        subreddit_str = "+".join(subreddits)
        subreddit = self.reddit.subreddit(subreddit_str)

        print(f"Scouting r/{subreddit_str} for '{search_query}'...")

        try:
            # Search logic
            for submission in subreddit.search(search_query, limit=limit, sort='new'):
                if check_deduplication(submission.id):
                    print(f"Skipping duplicate: {submission.id}")
                    continue

                post_data = {
                    "platform": "Reddit",
                    "external_post_id": submission.id,
                    "title": submission.title,
                    "content": submission.selftext,
                    "url": submission.url,
                    "author": str(submission.author)
                }
                
                # Save to DB
                # We combine title and body for the 'post_content' field
                full_content = f"Title: {submission.title}\nBody: {submission.selftext}\nURL: {submission.url}"
                
                save_interaction(
                    platform="Reddit",
                    external_post_id=submission.id,
                    post_content=full_content,
                    status="ARCHIVED"
                )
                
                found_posts.append(post_data)
                print(f"Archived: {submission.title[:30]}...")

        except Exception as e:
            print(f"Error fetching Reddit posts: {e}")

        return found_posts

    def like_post(self, external_post_id: str) -> bool:
        """
        Upvotes a post by ID.
        """
        try:
            submission = self.reddit.submission(id=external_post_id)
            submission.upvote()
            print(f"Upvoted post {external_post_id}")
            return True
        except Exception as e:
            print(f"Failed to upvote {external_post_id}: {e}")
            return False

# Singleton instance or factory can be used
reddit_scout = RedditScout()

