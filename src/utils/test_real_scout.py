import sys
import os
import shutil
sys.path.insert(0, os.getcwd())

from src.agents.twitter_scout import TwitterScout

def test_real_scout():
    print("Testing Real Data Scout with Auto-Login (Real Profile)...")
    
    # Use the default directory (Real App Data)
    # temp_dir = os.path.join(os.getcwd(), "twitter_auth_data_test")
    # if os.path.exists(temp_dir):
    #     shutil.rmtree(temp_dir)
        
    scout = TwitterScout() # Default dir
    scout.headless = False
    
    # Use a popular keyword to guarantee results if successful
    keywords = ["build in public"]
    
    try:
        results = scout.fetch_posts(keywords, limit=5)
        
        print(f"\nFound {len(results)} REAL tweets.")
        for tweet in results:
            print(f"- [{tweet['handle']}] {tweet['text'][:50]}...")
            
    except Exception as e:
        print(f"Test Failed: {e}")
        
    # Cleanup (optional, maybe keep for inspection if failed)
    # shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_real_scout()
