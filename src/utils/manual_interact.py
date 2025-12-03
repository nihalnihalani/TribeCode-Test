import sys
import os
import random
# Add src to path
sys.path.insert(0, os.getcwd())

from src.database import get_all_interactions
from src.agents.twitter_scout import twitter_scout

def manual_test():
    print("Fetching latest interaction from DB...")
    interactions = get_all_interactions(limit=1)
    
    if not interactions:
        print("No interactions found in DB. Run a scout first.")
        return

    target = interactions[0]
    print(f"Target Tweet: {target.external_post_id} | {target.post_content[:50]}...")
    
    # 1. Test Like
    print("\n--- Testing Like ---")
    # Enable headless=False temporarily for visual check if running locally, 
    # but we keep it as configured in class (default True) for now unless modified.
    # Hack: modify instance headless
    twitter_scout.headless = False 
    
    success_like = twitter_scout.like_post(target.external_post_id)
    print(f"Like Result: {success_like}")
    
    # 2. Test Comment
    print("\n--- Testing Comment ---")
    dummy_comment = f"Great insight! 🚀 #{random.randint(1000,9999)}"
    print(f"Posting comment: {dummy_comment}")
    
    success_comment = twitter_scout.comment_post(target.external_post_id, dummy_comment)
    print(f"Comment Result: {success_comment}")

if __name__ == "__main__":
    manual_test()

