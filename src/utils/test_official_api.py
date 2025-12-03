import os
import tweepy
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def test_official_api():
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    
    if not api_key or not api_secret:
        print("No API keys found in .env")
        return

    print("Testing Official Twitter API...")
    
    # Authenticate
    auth = tweepy.OAuthHandler(api_key, api_secret)
    # We might need access token/secret if using user context, 
    # but for app-only (search), usually Bearer token is used with Client in API v2.
    
    # Try API v2 Client (preferred for search)
    # We need a BEARER_TOKEN for app-only auth usually.
    # Or we can generate it from key/secret.
    
    try:
        # Using v2 Client
        client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret)
        
        # Search Recent (Basic tier access)
        query = "vibe coding -is:retweet"
        print(f"Searching for: {query}")
        
        tweets = client.search_recent_tweets(query=query, max_results=10, tweet_fields=['created_at', 'author_id', 'public_metrics'])
        
        if tweets.data:
            print(f"Found {len(tweets.data)} tweets via Official API:")
            for tweet in tweets.data:
                print(f"- {tweet.text[:50]}...")
        else:
            print("No tweets found (or API limit reached/Not allowed on this tier).")
            
    except Exception as e:
        print(f"Official API Error: {e}")

if __name__ == "__main__":
    test_official_api()

