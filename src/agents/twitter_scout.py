import os
import tweepy
from typing import List, Dict
from dotenv import load_dotenv
from src.database import save_interaction

load_dotenv()

class TwitterScout:
    def __init__(self):
        self.client = None
        self.api_tier = "free"  # Assumed based on user input
        self._authenticate()

    def _authenticate(self):
        try:
            api_key = os.getenv("TWITTER_API_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

            if not (api_key and api_secret):
                print("Twitter credentials missing. Skipping auth.")
                return

            # V2 Client for modern endpoints
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            print("Twitter Client initialized.")
        except Exception as e:
            print(f"Twitter Auth Error: {e}")

    def fetch_posts(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """
        Attempts to fetch posts. 
        NOTE: Twitter API Free Tier does NOT support Search Tweets (Read).
        This function is a stub for Basic/Pro tiers.
        """
        print("\n[Twitter Scout] Fetching posts...")
        
        if self.api_tier == "free":
            print("⚠️  WARNING: Twitter Free Tier does not support 'Search Tweets' (Reading).")
            print("   To enable this, upgrade to Basic Tier ($100/mo) or Enterprise.")
            print("   Returning empty list for now.")
            return []

        # Logic for Basic Tier (if enabled later)
        found_tweets = []
        # Combine keywords with OR for broader search
        query = " OR ".join(keywords) + " -is:retweet"
        
        try:
            if self.client:
                response = self.client.search_recent_tweets(
                    query=query, 
                    max_results=min(limit, 100), # API limits
                    tweet_fields=['created_at', 'author_id', 'text']
                )
                
                if response.data:
                    for tweet in response.data:
                        save_interaction(
                            platform="Twitter",
                            external_post_id=str(tweet.id),
                            post_content=tweet.text,
                            status="ARCHIVED"
                        )
                        found_tweets.append({"id": tweet.id, "text": tweet.text})
                        print(f"Archived Tweet: {tweet.text[:30]}...")
                        
            return found_tweets
            
        except Exception as e:
            print(f"Twitter Fetch Error: {e}")
            return []

    def like_post(self, tweet_id: str) -> bool:
        """
        Likes a tweet.
        NOTE: Free Tier generally restricts this too, but sometimes write-access allows it.
        """
        print(f"[Twitter Scout] Attempting to like tweet {tweet_id}...")
        
        try:
            if self.client:
                # Retrieve own user ID first if not cached
                me = self.client.get_me()
                if me.data:
                    my_id = me.data.id
                    self.client.like(tweet_id=tweet_id)
                    print(f"Liked tweet {tweet_id}")
                    return True
        except Exception as e:
            print(f"Twitter Like Error (Likely Tier Restriction): {e}")
            return False

    def comment_post(self, tweet_id: str, text: str) -> bool:
        """
        Replies to a tweet.
        """
        print(f"[Twitter Scout] Attempting to reply to tweet {tweet_id}...")
        try:
            if self.client:
                self.client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
                print(f"Replied to {tweet_id}: {text}")
                return True
        except Exception as e:
            print(f"Twitter Reply Error: {e}")
            return False

twitter_scout = TwitterScout()
