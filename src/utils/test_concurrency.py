import threading
import time
import sys
import os
from queue import Queue

sys.path.insert(0, os.getcwd())
from src.agents.twitter_scout import twitter_scout

def test_concurrency():
    print("Testing Concurrent Browser Access (Locking Mechanism)...")
    
    results_queue = Queue()
    
    def task_scout():
        try:
            print("[Thread-1] Starting Scout Task...")
            # This should take time and hold the lock
            # We'll use a real fetch but with limit=1 to be relatively quick but slow enough to overlap
            res = twitter_scout.fetch_posts(["concurrency test"], limit=1)
            print("[Thread-1] Scout Finished.")
            results_queue.put(("scout", True))
        except Exception as e:
            print(f"[Thread-1] Scout Failed: {e}")
            results_queue.put(("scout", False))

    def task_like():
        # Wait a bit to ensure Scout has started and grabbed lock
        time.sleep(2) 
        print("[Thread-2] Starting Like Task (Should wait for lock)...")
        try:
            # We'll try to like a fake ID, just to test lock acquisition
            # It should wait until Scout releases lock
            start_time = time.time()
            twitter_scout.like_post("test_post_concurrency")
            duration = time.time() - start_time
            print(f"[Thread-2] Like Finished (Duration: {duration:.2f}s).")
            
            # If lock worked, duration should be significant (scout takes time)
            # If it didn't wait, it would fail immediately or crash browser
            results_queue.put(("like", True))
        except Exception as e:
            print(f"[Thread-2] Like Failed: {e}")
            results_queue.put(("like", False))

    # Start threads
    t1 = threading.Thread(target=task_scout)
    t2 = threading.Thread(target=task_like)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    print("\nConcurrency Test Completed.")
    
    # Verify
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
        
    print(f"Results: {results}")

if __name__ == "__main__":
    # Ensure we are in a clean state
    try:
        os.system("rm -f twitter_auth_data/SingletonLock")
    except:
        pass
        
    test_concurrency()

