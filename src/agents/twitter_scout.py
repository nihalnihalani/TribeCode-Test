import os
import time
import random
from typing import List, Dict
from playwright.sync_api import sync_playwright
from src.database import save_interaction

class TwitterScout:
    def __init__(self):
        self.user_data_dir = os.path.join(os.getcwd(), "twitter_auth_data")
        self.headless = True # Set to False if debugging is needed

    def fetch_posts(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """
        Fetches posts using Playwright with a persistent profile.
        """
        print(f"\n[Twitter Scout] Fetching posts for keywords: {keywords}")
        
        found_tweets = []
        
        # Combine keywords (Playwright search logic)
        # Twitter search: "keyword1 OR keyword2"
        query = " OR ".join(f'"{k}"' for k in keywords)
        search_url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
        
        print(f"  Search URL: {search_url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 720}
                )
                
                page = browser.new_page()
                page.goto(search_url)
                
                # Wait for tweets to load
                try:
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                except Exception:
                    print("  Timeout waiting for tweets. Maybe no results or login required?")
                    # Capture screenshot for debug (optional, but good for MVP)
                    # page.screenshot(path="debug_twitter_fetch.png")
                    browser.close()
                    return []

                # Scroll a bit to load more if needed
                for _ in range(3):
                    page.mouse.wheel(0, 1000)
                    time.sleep(1)

                tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
                print(f"  Found {len(tweet_elements)} potential tweets (limiting to {limit})")

                count = 0
                for tweet_el in tweet_elements:
                    if count >= limit:
                        break
                        
                    try:
                        # Extract ID from anchor href (usually /username/status/ID)
                        # There are multiple links, find the one with /status/
                        # Better: User-Name -> time element -> href
                        time_el = tweet_el.query_selector('time')
                        if not time_el:
                            continue
                        
                        post_link_el = time_el.query_selector('..') # Parent of time is usually the link
                        href = post_link_el.get_attribute('href') if post_link_el else ""
                        
                        if "status" not in href:
                            # Fallback: search all links in tweet
                            links = tweet_el.query_selector_all('a')
                            for link in links:
                                h = link.get_attribute('href')
                                if h and "/status/" in h and "/photo/" not in h:
                                    href = h
                                    break
                        
                        if not href:
                            continue
                            
                        # href format: /Username/status/123456789
                        tweet_id = href.split('/status/')[-1].split('?')[0]
                        
                        # Extract Text
                        text_el = tweet_el.query_selector('div[data-testid="tweetText"]')
                        text = text_el.inner_text() if text_el else "[No Text / Image Only]"
                        
                        # Extract Author (Handle)
                        user_el = tweet_el.query_selector('div[data-testid="User-Name"]')
                        author = user_el.inner_text().split('\n')[0] if user_el else "Unknown"

                        # Deduplication & Save
                        # Note: we save with ARCHIVED status initially
                        saved = save_interaction(
                            platform="Twitter",
                            external_post_id=tweet_id,
                            post_content=text,
                            status="ARCHIVED"
                        )
                        
                        found_tweets.append({"id": tweet_id, "text": text, "author": author})
                        print(f"  Archived Tweet {tweet_id}: {text[:30]}...")
                        count += 1
                        
                    except Exception as e:
                        print(f"  Error parsing tweet: {e}")
                        continue
                
                browser.close()
                return found_tweets

        except Exception as e:
            print(f"Twitter Scout Error: {e}")
            return []

    def like_post(self, tweet_id: str) -> bool:
        """
        Likes a tweet by navigating to it and clicking the heart.
        """
        print(f"[Twitter Scout] Attempting to like tweet {tweet_id}...")
        url = f"https://twitter.com/i/web/status/{tweet_id}"
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 720}
                )
                
                page = browser.new_page()
                page.goto(url)
                
                # Wait for Like button
                # Selector for like button: data-testid="like"
                try:
                    like_button = page.wait_for_selector('button[data-testid="like"]', timeout=10000)
                    if like_button:
                        like_button.click()
                        print(f"  Clicked Like on {tweet_id}")
                        time.sleep(1) # Grace period
                        browser.close()
                        return True
                    else:
                        # Check if already liked? data-testid="unlike"
                        unlike_button = page.query_selector('button[data-testid="unlike"]')
                        if unlike_button:
                            print(f"  Tweet {tweet_id} already liked.")
                            browser.close()
                            return True
                            
                except Exception as e:
                    print(f"  Could not find like button: {e}")
                
                browser.close()
                return False
                
        except Exception as e:
            print(f"Twitter Like Error: {e}")
            return False

    def comment_post(self, tweet_id: str, text: str) -> bool:
        """
        Replies to a tweet.
        """
        print(f"[Twitter Scout] Attempting to reply to tweet {tweet_id}...")
        url = f"https://twitter.com/i/web/status/{tweet_id}"
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 720}
                )
                
                page = browser.new_page()
                page.goto(url)
                
                # 1. Click Reply Box (often "Post your reply")
                # Selector: div[data-testid="tweetTextarea_0"] is the input.
                # Usually we can just type into the contenteditable.
                
                try:
                    editor = page.wait_for_selector('div[data-testid="tweetTextarea_0"]', timeout=10000)
                    if editor:
                        editor.click()
                        editor.fill(text)
                        
                        # Click Reply Button
                        # button[data-testid="tweetButtonInline"]
                        submit_btn = page.wait_for_selector('button[data-testid="tweetButtonInline"]', timeout=5000)
                        if submit_btn:
                            submit_btn.click()
                            print(f"  Replied to {tweet_id}")
                            time.sleep(2)
                            browser.close()
                            return True
                            
                except Exception as e:
                    print(f"  Reply failed: {e}")
                
                browser.close()
                return False

        except Exception as e:
            print(f"Twitter Reply Error: {e}")
            return False

twitter_scout = TwitterScout()
