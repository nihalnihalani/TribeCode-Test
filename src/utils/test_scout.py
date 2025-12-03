import sys
import os
sys.path.insert(0, os.getcwd())

from src.agents.twitter_scout import twitter_scout

def test_search():
    print("Testing Twitter Search via Playwright (Headful)...")
    keywords = ["vibe coding", "build in public"]
    
    # Use headless=False to match the login session environment
    twitter_scout.headless = False
    
    try:
        results = twitter_scout.fetch_posts(keywords, limit=5)
        
        print(f"\nFound {len(results)} tweets.")
        for tweet in results:
            print(f"- [{tweet['handle']}] {tweet['text'][:50]}...")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_search()
