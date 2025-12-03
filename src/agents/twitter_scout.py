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
        Extracts: text, author, handle, metrics, media.
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
                        # Extract handle from href
                        parts = href.split('/')
                        if len(parts) >= 2:
                            handle = "@" + parts[1]
                            tweet_id = href.split('/status/')[-1].split('?')[0]
                            post_url = f"https://twitter.com{href}"
                        else:
                            continue
                        
                        # Extract Text
                        text_el = tweet_el.query_selector('div[data-testid="tweetText"]')
                        text = text_el.inner_text() if text_el else "[No Text / Image Only]"
                        
                        # Extract Author Name
                        user_el = tweet_el.query_selector('div[data-testid="User-Name"]')
                        author_name = "Unknown"
                        if user_el:
                            # usually "Name\n@handle\n·\nTime"
                            raw_user_text = user_el.inner_text()
                            author_name = raw_user_text.split('\n')[0]

                        # Extract Metrics (Likes, Retweets, Replies)
                        # Selectors: [data-testid="reply"], [data-testid="retweet"], [data-testid="like"]
                        # They usually contain an aria-label with the count, or text inside.
                        metrics = {"replies": 0, "retweets": 0, "likes": 0}
                        
                        def get_metric(testid):
                            el = tweet_el.query_selector(f'[data-testid="{testid}"]')
                            if el:
                                txt = el.inner_text() or "0"
                                # Convert "1.2K" to 1200 if needed, but storing string is fine for display
                                return txt.strip()
                            return "0"

                        metrics["replies"] = get_metric("reply")
                        metrics["retweets"] = get_metric("retweet")
                        metrics["likes"] = get_metric("like")
                        
                        # Extract Media (First Image)
                        media_url = None
                        img_el = tweet_el.query_selector('div[data-testid="tweetPhoto"] img')
                        if img_el:
                            media_url = img_el.get_attribute('src')

                        # Deduplication & Save
                        saved = save_interaction(
                            platform="Twitter",
                            external_post_id=tweet_id,
                            post_content=text,
                            status="ARCHIVED",
                            author_name=author_name,
                            author_handle=handle,
                            post_url=post_url,
                            metrics=metrics,
                            media_url=media_url
                        )
                        
                        found_tweets.append({
                            "id": tweet_id, 
                            "text": text, 
                            "author": author_name,
                            "handle": handle,
                            "metrics": metrics
                        })
                        print(f"  Archived Tweet {tweet_id} by {handle}: {text[:30]}...")
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
                # Twitter updated their selectors:
                # The main reply area often has a placeholder "Post your reply"
                # and is a contenteditable div.
                
                try:
                    # Try multiple selectors for robustness
                    editor_selectors = [
                        'div[data-testid="tweetTextarea_0"]',
                        'div[aria-label="Post text"]',
                        'div[contenteditable="true"]'
                    ]
                    
                    editor = None
                    for sel in editor_selectors:
                        try:
                            editor = page.wait_for_selector(sel, timeout=5000)
                            if editor:
                                break
                        except:
                            continue
                            
                    if editor:
                        editor.click()
                        editor.fill(text)
                        
                        # Click Reply Button
                        submit_btn = page.wait_for_selector('button[data-testid="tweetButtonInline"]', timeout=5000)
                        if submit_btn:
                            # Check if disabled
                            if submit_btn.is_disabled():
                                print("  Reply button disabled (maybe text too long or empty?)")
                            else:
                                submit_btn.click()
                                print(f"  Replied to {tweet_id}")
                                time.sleep(2)
                                browser.close()
                                return True
                    else:
                        print("  Could not find reply editor.")
                            
                except Exception as e:
                    print(f"  Reply failed: {e}")
                
                browser.close()
                return False

        except Exception as e:
            print(f"Twitter Reply Error: {e}")
            return False

twitter_scout = TwitterScout()
