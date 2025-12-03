import os
import time
import random
from typing import List, Dict
from playwright.sync_api import sync_playwright
from src.database import save_interaction

class TwitterScout:
    def __init__(self, user_data_dir: str = None):
        if user_data_dir:
            self.user_data_dir = user_data_dir
        else:
            self.user_data_dir = os.path.join(os.getcwd(), "twitter_auth_data")
        self.headless = False # Visible for debugging/login checking

    def login(self, page):
        """
        Attempts to log in to Twitter via Username/Password or Google.
        """
        print("  [Login] Checking for login requirement...")
        
        try:
            # Check for login indicators
            content = page.content()
            if "Sign in to X" in content or "Log in" in content:
                print("  [Login] Login screen detected.")
                
                # Try Standard Login first (Username/Password)
                tw_username = os.getenv("TWITTER_USERNAME")
                tw_password = os.getenv("TWITTER_PASSWORD")
                
                if tw_username and tw_password:
                    print(f"  [Login] Attempting standard login for {tw_username}...")
                    try:
                        # Sometimes we need to click a "Log in" button to see the form if we are on a landing page
                        login_button = page.query_selector('a[href="/login"]')
                        if login_button:
                            print("  [Login] Clicking 'Log in' link...")
                            login_button.click()
                            time.sleep(2)

                        # 1. Find Username field
                        # It's usually an input with autocomplete="username" or name="text"
                        print("  [Login] Looking for username input...")
                        user_input = None
                        try:
                            user_input = page.wait_for_selector('input[autocomplete="username"]', timeout=5000)
                        except:
                            pass
                        
                        if not user_input:
                            try:
                                user_input = page.wait_for_selector('input[name="text"]', timeout=5000)
                            except:
                                pass
                        
                        if user_input:
                            print("  [Login] Entering Username...")
                            user_input.fill(tw_username)
                            user_input.press("Enter")
                            
                            time.sleep(2)
                            
                            # Check for unusual activity verification (sometimes asks for phone/email)
                            # If we see another text input but no password input yet
                            try:
                                ver_input = page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=2000)
                                if ver_input:
                                    print("  [Login] unusual activity check detected. Entering username/email again...")
                                    ver_input.fill(tw_username) # Usually wants username or email
                                    ver_input.press("Enter")
                                    time.sleep(2)
                            except:
                                pass

                            # 2. Wait for Password field
                            print("  [Login] Waiting for Password field...")
                            pass_input = page.wait_for_selector('input[name="password"]', timeout=5000)
                            
                            if pass_input:
                                print("  [Login] Entering Password...")
                                pass_input.fill(tw_password)
                                pass_input.press("Enter")
                                
                                # Wait for success
                                print("  [Login] Waiting for authentication...")
                                try:
                                    page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                                    print("  [Login] Success! Tweets visible.")
                                    return
                                except:
                                    print("  [Login] Wait for tweets timed out, but proceeding...")
                                    time.sleep(3)
                                return
                                
                    except Exception as e:
                        print(f"  [Login] Standard login attempt failed: {e}")

                # Fallback to Google Login
                email = os.getenv("GOOGLE_EMAIL")
                password = os.getenv("GOOGLE_PASSWORD")
                
                if not email or not password:
                    print("  [Login] No Google credentials in .env! Cannot auto-login.")
                    return
                
                print("  [Login] Attempting Google login...")
                # Click "Sign in with Google"
                # Note: Twitter's Google Sign In often opens a popup window.
                
                # We need to handle the popup
                with page.expect_popup() as popup_info:
                    # Find the button. It might be an iframe, so we try broad text matching first
                    # or specific data-testid if known. 
                    # 'iframe' is common for Google Identity.
                    
                    # Try clicking the Google button
                    # Usually has 'Sign in with Google' text
                    google_btn = page.get_by_text("Sign in with Google")
                    if google_btn.count() > 0:
                        print("  [Login] Clicking 'Sign in with Google'...")
                        google_btn.first.click()
                    else:
                        # Fallback: try clicking 'Log in' then finding Google
                        print("  [Login] 'Sign in with Google' not found immediately. Trying 'Log in' link...")
                        
                        # Try multiple selectors for Log in button
                        login_btn = None
                        try:
                            login_btn = page.wait_for_selector('a[href="/login"]', timeout=5000)
                        except:
                            try:
                                login_btn = page.get_by_role("button", name="Log in").first
                            except:
                                pass
                        
                        if login_btn:
                            print("  [Login] Found 'Log in' button/link. Clicking...")
                            login_btn.click()
                            time.sleep(3)
                            # Now try finding Google button again
                            try:
                                google_btn = page.wait_for_selector('iframe', timeout=5000) # Google often in iframe
                                # This is tricky. Let's just look for text again in new page
                                page.get_by_text("Sign in with Google").first.click()
                            except:
                                print("  [Login] Could not find Google sign in after clicking Log in.")
                        else:
                             print("  [Login] Could not find 'Log in' button.")
                
                popup = popup_info.value
                print("  [Login] Google Popup opened.")
                
                # Interact with Google Popup
                popup.wait_for_load_state()
                
                # 1. Email
                print("  [Login] Entering Email...")
                email_input = popup.wait_for_selector('input[type="email"]', timeout=10000)
                email_input.fill(email)
                popup.keyboard.press("Enter")
                
                # Wait for password field
                time.sleep(3)
                
                # 2. Password
                print("  [Login] Entering Password...")
                pass_input = popup.wait_for_selector('input[type="password"]', timeout=10000)
                pass_input.fill(password)
                popup.keyboard.press("Enter")
                
                # Wait for popup to close (success)
                print("  [Login] Waiting for authentication...")
                popup.wait_for_event("close", timeout=30000)
                print("  [Login] Popup closed. Authentication likely successful.")
                
                # Wait for main page to reload/redirect
                page.wait_for_load_state()
                time.sleep(5)
                
        except Exception as e:
            print(f"  [Login] Auto-login attempt failed (or not needed): {e}")

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
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox"
                    ],
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                
                page = browser.new_page()
                
                # 1. Navigate to home to set cookies/verify session
                print("  Navigating to Twitter Home...")
                try:
                    page.goto("https://twitter.com/home", timeout=30000)
                    time.sleep(3)
                except Exception as e:
                    print(f"  Warning: Home page navigation failed: {e}")

                print(f"  Navigating to Search: {search_url}")
                page.goto(search_url)
                
                # Wait for tweets to load
                try:
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                except Exception:
                    print("  Timeout waiting for tweets. Checking for login requirement...")
                    self.login(page)
                    
                    # Retry waiting for tweets after login attempt
                    try:
                        print("  Retrying wait for tweets...")
                        page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                    except Exception:
                        print("  Still no tweets found. Aborting.")
                        # Capture screenshot for debug
                        page.screenshot(path="debug_twitter_fetch.png")
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
        print(f"[Twitter Scout] Attempting to like tweet {tweet_id}")
        
        # Check if this is a mock/test ID (e.g. from unit tests)
        if "test_post" in tweet_id:
            print("  Skipping like on test ID")
            return False
            
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
                print(f"  Navigating to {url}")
                page.goto(url)
                
                # Wait for tweet content to verify page load
                try:
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
                except:
                    print("  Tweet not found or failed to load.")
                    browser.close()
                    return False
                
                # Wait for Like button
                # Selectors can be tricky. 'like' or 'unlike'
                try:
                    # Check if already liked (unlike button exists)
                    if page.query_selector('button[data-testid="unlike"]'):
                        print(f"  Tweet {tweet_id} is already liked.")
                        browser.close()
                        return True
                        
                    like_button = page.wait_for_selector('button[data-testid="like"]', timeout=5000)
                    if like_button:
                        like_button.scroll_into_view_if_needed()
                        like_button.click()
                        print(f"  Clicked Like on {tweet_id}")
                        time.sleep(1) # Grace period
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
        print(f"[Twitter Scout] Attempting to reply to tweet {tweet_id}")
        
        if "test_post" in tweet_id:
            print("  Skipping comment on test ID")
            return False
            
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
                print(f"  Navigating to {url}")
                page.goto(url)
                
                # Wait for tweet to ensure we are on the right page
                try:
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
                except:
                    print("  Tweet page failed to load.")
                    browser.close()
                    return False
                
                # 1. Click Reply Input (The inline one usually at bottom of tweet or "Post your reply")
                try:
                    # Try clicking the reply div first to focus
                    # 'div.public-DraftEditor-content' is the editor content area
                    
                    # First, find the editor. On status page, it's usually visible.
                    # Try to click the "Reply" placeholder text if visible
                    placeholder = page.query_selector('div[data-testid="tweetTextarea_0_label"]')
                    if placeholder:
                        placeholder.click()
                        
                    editor = page.wait_for_selector('div.public-DraftEditor-content', timeout=5000)
                    
                    if editor:
                        editor.click()
                        # Type properly
                        page.keyboard.type(text, delay=50) 
                        
                        time.sleep(1)
                        
                        # Click Reply Button
                        submit_btn = page.wait_for_selector('button[data-testid="tweetButtonInline"]', timeout=5000)
                        if submit_btn:
                            if submit_btn.is_disabled():
                                print("  Reply button disabled.")
                            else:
                                submit_btn.click()
                                print(f"  Replied to {tweet_id}")
                                time.sleep(3) # Wait for post to submit
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
