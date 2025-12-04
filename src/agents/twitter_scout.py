import os
import time
import random
import threading
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page
from src.database import save_interaction, get_all_interactions
from src.agents.interaction_agent import interaction_agent

class TwitterScout:
    # Class-level lock to prevent multiple Playwright instances from conflicting
    _lock = threading.Lock()

    def __init__(self, user_data_dir: str = None):
        if user_data_dir:
            self.user_data_dir = user_data_dir
        else:
            self.user_data_dir = os.path.join(os.getcwd(), "twitter_auth_data")
        self.headless = False # Visible for debugging/login checking

    def _get_browser_context(self, p):
        """Helper to launch context with consistent settings."""
        return p.chromium.launch_persistent_context(
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
                            
                            # Check for unusual activity verification
                            try:
                                ver_input = page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=2000)
                                if ver_input:
                                    print("  [Login] unusual activity check detected. Entering username/email again...")
                                    ver_input.fill(tw_username)
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
                                    try:
                                        page.context.storage_state(path=os.path.join(self.user_data_dir, "twitter_state.json"))
                                    except: pass
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
                
                with page.expect_popup() as popup_info:
                    google_btn = page.get_by_text("Sign in with Google")
                    if google_btn.count() > 0:
                        print("  [Login] Clicking 'Sign in with Google'...")
                        google_btn.first.click()
                    else:
                        print("  [Login] 'Sign in with Google' not found immediately. Trying 'Log in' link...")
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
                            try:
                                google_btn = page.wait_for_selector('iframe', timeout=5000)
                                page.get_by_text("Sign in with Google").first.click()
                            except:
                                print("  [Login] Could not find Google sign in after clicking Log in.")
                        else:
                             print("  [Login] Could not find 'Log in' button.")
                
                popup = popup_info.value
                print("  [Login] Google Popup opened.")
                
                popup.wait_for_load_state()
                
                # 1. Email
                print("  [Login] Entering Email...")
                email_input = popup.wait_for_selector('input[type="email"]', timeout=10000)
                email_input.fill(email)
                popup.keyboard.press("Enter")
                
                time.sleep(3)
                
                # 2. Password
                print("  [Login] Entering Password...")
                pass_input = popup.wait_for_selector('input[type="password"]', timeout=10000)
                pass_input.fill(password)
                popup.keyboard.press("Enter")
                
                print("  [Login] Waiting for authentication...")
                popup.wait_for_event("close", timeout=30000)
                print("  [Login] Popup closed. Authentication likely successful.")
                
                page.wait_for_load_state()
                time.sleep(5)
                try:
                    page.context.storage_state(path=os.path.join(self.user_data_dir, "twitter_state.json"))
                except: pass
                
        except Exception as e:
            print(f"  [Login] Auto-login attempt failed (or not needed): {e}")

    def ensure_logged_in(self, page):
        """
        Soft check for login status. Navigates to home first.
        Only triggers full login flow if necessary.
        """
        print("  [Login] Checking login status...")
        try:
            # Soft check: Go to home
            page.goto("https://twitter.com/home", timeout=30000)
            time.sleep(3)
            
            # Check if we are on home or redirected to login
            if "login" in page.url:
                 print("  [Login] Redirected to login page.")
                 self.login(page)
            elif page.query_selector('[data-testid="SideNav_NewTweet_Button"]') or "home" in page.url:
                print("  [Login] Already logged in.")
            else:
                # Check for other logged-in indicators
                if page.query_selector('[data-testid="AppTabBar_Home_Link"]'):
                     print("  [Login] Already logged in (Home link found).")
                else:
                    print("  [Login] Status unclear, attempting login check...")
                    self.login(page)

        except Exception as e:
            print(f"  Warning: Login check failed: {e}")
            self.login(page)

    def fetch_posts(self, keywords: List[str], limit: int = 10, tag: str = None) -> List[Dict]:
        """
        Fetches posts using Playwright with a persistent profile.
        """
        if not self._lock.acquire(timeout=60):
            print("[Twitter Scout] Could not acquire lock. Skipping fetch.")
            return []
            
        try:
            print(f"\n[Twitter Scout] Fetching posts for keywords: {keywords}")
            
            found_tweets = []
            query = " OR ".join(f'"{k}"' for k in keywords)
            search_url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
            print(f"  Search URL: {search_url}")

            # Use tag if provided, otherwise try to infer if single keyword
            current_tag = tag if tag else (keywords[0] if len(keywords) == 1 else None)

            try:
                with sync_playwright() as p:
                    browser = self._get_browser_context(p)
                    page = browser.new_page()
                    
                    # Login Check
                    self.ensure_logged_in(page)

                    print(f"  Navigating to Search: {search_url}")
                    page.goto(search_url)
                    
                    try:
                        page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                    except Exception:
                        print("  Timeout waiting for tweets. Checking for login requirement...")
                        self.login(page)
                        try:
                            page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                        except Exception:
                            print("  Still no tweets found. Aborting.")
                            browser.close()
                            return []

                    # Scroll
                    for _ in range(3):
                        page.mouse.wheel(0, 1000)
                        time.sleep(1)

                    tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
                    print(f"  Found {len(tweet_elements)} potential tweets (limiting to {limit})")

                    count = 0
                    for tweet_el in tweet_elements:
                        if count >= limit:
                            break
                        
                        # Parsing Logic (Inline for brevity, usually shared)
                        try:
                            time_el = tweet_el.query_selector('time')
                            if not time_el: continue
                            
                            post_link_el = time_el.query_selector('..')
                            href = post_link_el.get_attribute('href') if post_link_el else ""
                            
                            if "status" not in href:
                                links = tweet_el.query_selector_all('a')
                                for link in links:
                                    h = link.get_attribute('href')
                                    if h and "/status/" in h and "/photo/" not in h:
                                        href = h
                                        break
                            
                            if not href: continue
                            
                            parts = href.split('/')
                            if len(parts) >= 2:
                                handle = "@" + parts[1]
                                tweet_id = href.split('/status/')[-1].split('?')[0]
                                post_url = f"https://twitter.com{href}"
                            else:
                                continue
                            
                            text_el = tweet_el.query_selector('div[data-testid="tweetText"]')
                            text = text_el.inner_text() if text_el else "[No Text / Image Only]"
                            
                            user_el = tweet_el.query_selector('div[data-testid="User-Name"]')
                            author_name = "Unknown"
                            if user_el:
                                raw_user_text = user_el.inner_text()
                                author_name = raw_user_text.split('\n')[0]

                            metrics = {"replies": 0, "retweets": 0, "likes": 0}
                            def get_metric(testid):
                                el = tweet_el.query_selector(f'[data-testid="{testid}"]')
                                return el.inner_text().strip() if el else "0"

                            metrics["replies"] = get_metric("reply")
                            metrics["retweets"] = get_metric("retweet")
                            metrics["likes"] = get_metric("like")
                            
                            # Check for image/media
                            media_url = None
                            img_el = tweet_el.query_selector('div[data-testid="tweetPhoto"] img')
                            if img_el: media_url = img_el.get_attribute('src')
                            
                            # If we are skipping images, check now
                            if media_url:
                                print(f"  Skipping Tweet {tweet_id} (Has Image)")
                                continue

                            interaction = save_interaction(
                                platform="Twitter",
                                external_post_id=tweet_id,
                                post_content=text,
                                status="ARCHIVED",
                                author_name=author_name,
                                author_handle=handle,
                                post_url=post_url,
                                metrics=metrics,
                                media_url=media_url,
                                tag=current_tag
                            )

                            # Generate comment if missing (Draft Mode)
                            if not interaction.bot_comment:
                                try:
                                    context_posts = get_all_interactions(limit=10)
                                    draft_comment = interaction_agent.generate_comment(interaction, context_posts)
                                    if draft_comment:
                                        interaction.bot_comment = draft_comment
                                        save_interaction(
                                            platform="Twitter",
                                            external_post_id=tweet_id,
                                            post_content=text,
                                            bot_comment=draft_comment
                                        )
                                        print(f"  [Auto-Draft] Comment generated: {draft_comment}")
                                except Exception as e:
                                    print(f"  [Auto-Draft] Failed to generate comment: {e}")
                            
                            found_tweets.append({
                                "id": tweet_id, "text": text, "author": author_name,
                                "handle": handle, "metrics": metrics
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
        finally:
            self._lock.release()

    def batch_engage(self, keywords: List[str], limit: int, auto_like: bool, auto_comment: bool, interaction_agent, tag: str = None) -> int:
        """
        Fetches posts AND engages (like/comment) in a SINGLE session.
        """
        if not self._lock.acquire(timeout=60):
            print("[Twitter Scout] Could not acquire lock. Skipping batch engage.")
            return 0
            
        try:
            print(f"\n[Twitter Scout] Starting BATCH ENGAGE (Auto-Like={auto_like}, Auto-Comment={auto_comment})")
            
            query = " OR ".join(f'"{k}"' for k in keywords)
            search_url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
            
            # Use tag if provided, otherwise try to infer if single keyword
            current_tag = tag if tag else (keywords[0] if len(keywords) == 1 else None)
            
            processed_count = 0

            try:
                with sync_playwright() as p:
                    browser = self._get_browser_context(p)
                    page = browser.new_page()
                    
                    # 1. Login Check
                    self.ensure_logged_in(page)

                    # 2. Search
                    print(f"  Navigating to Search: {search_url}")
                    page.goto(search_url)
                    
                    try:
                        page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                    except Exception:
                        self.login(page)
                        try:
                            page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                        except:
                            print("  No tweets found.")
                            browser.close()
                            return 0

                    for _ in range(3):
                        page.mouse.wheel(0, 1000)
                        time.sleep(1)

                    tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
                    
                    # We need to capture the IDs first because navigating away will destroy elements
                    tweet_data_list = []
                    
                    print(f"  Found {len(tweet_elements)} potential tweets.")
                    
                    count = 0
                    for tweet_el in tweet_elements:
                        if count >= limit: break
                        try:
                            # Basic parsing just to get ID
                            time_el = tweet_el.query_selector('time')
                            if not time_el: continue
                            post_link_el = time_el.query_selector('..')
                            href = post_link_el.get_attribute('href') if post_link_el else ""
                            if "status" not in href: continue
                            
                            tweet_id = href.split('/status/')[-1].split('?')[0]
                            
                            # Skip if we can't find ID
                            if not tweet_id: continue
                            
                            tweet_data_list.append({"id": tweet_id, "href": href})
                            count += 1
                        except:
                            continue

                    print(f"  Processing {len(tweet_data_list)} tweets for engagement...")

                    # 3. Loop and Engage
                    for item in tweet_data_list:
                        tweet_id = item["id"]
                        print(f"  --- Processing Tweet {tweet_id} ---")
                        
                        # We must visit the single tweet page to engage reliably
                        # This also allows us to parse full details cleanly if we wanted to update them
                        
                        # First, ensure we have the interaction saved/updated
                        # (We might re-fetch details on the single page or just use what we have)
                        # For this v1, let's just navigate and do the work.
                        
                        try:
                            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
                            page.goto(tweet_url)
                            page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
                            
                            # Extract Text for context (re-parse)
                            text = "[No Text]"
                            try:
                                text_el = page.query_selector('div[data-testid="tweetText"]')
                                if text_el: text = text_el.inner_text()
                            except: pass
                            
                            # Check for Media on single page view
                            has_media = False
                            if page.query_selector('div[data-testid="tweetPhoto"]'):
                                has_media = True
                            
                            if has_media and auto_comment:
                                print(f"  Skipping comment on {tweet_id} due to image/media.")
                                # We can still like it though? User said "don't post a comment or reply"
                                # Let's skip the whole engagement if it has media to be safe, or just comment?
                                # "if the tweet has reference to image don't post a comment or reply"
                                # Implementation: We will still Archive it, maybe Like it? 
                                # Let's assume we skip comment only.
                                auto_comment = False 

                            # Save/Update DB first
                            interaction = save_interaction(
                                platform="Twitter",
                                external_post_id=tweet_id,
                                post_content=text,
                                status="ARCHIVED",
                                post_url=tweet_url,
                                tag=current_tag
                            )
                            
                            # Like
                            if auto_like:
                                self.like_post(tweet_id, page=page)
                            
                            # Comment
                            if auto_comment:
                                # Check if we already commented
                                if interaction.bot_comment:
                                    print("  Already commented on this tweet. Skipping.")
                                else:
                                    # Generate Context
                                    context_posts = get_all_interactions(limit=10)
                                    comment_text = interaction_agent.generate_comment(interaction, context_posts)
                                    
                                    if comment_text:
                                        print(f"  Generated Comment: {comment_text}")
                                        success = self.comment_post(tweet_id, comment_text, page=page)
                                        if success:
                                            interaction.bot_comment = comment_text
                                            interaction.status = "POSTED"
                                            # Update DB? save_interaction updates fields passed, but here we updated object
                                            # We should call save_interaction again or update manually.
                                            # save_interaction handles updates if ID exists.
                                            save_interaction(
                                                platform="Twitter",
                                                external_post_id=tweet_id,
                                                post_content=text,
                                                status="POSTED",
                                                bot_comment=comment_text,
                                                tag=current_tag
                                            )
                            
                            processed_count += 1
                            time.sleep(random.uniform(2, 5)) # Human pause
                            
                        except Exception as e:
                            print(f"  Error processing tweet {tweet_id}: {e}")
                            continue

                    print("  Batch engagement finished. Closing browser in 5 seconds...")
                    time.sleep(5)
                    browser.close()
                    return processed_count

            except Exception as e:
                print(f"Batch Engage Error: {e}")
                return 0
        finally:
            self._lock.release()

    def engage_post(self, tweet_id: str, text: str, like: bool = True, page: Page = None) -> bool:
        """
        Likes and replies to a tweet in a single session.
        """
        if page is None:
            # Standalone wrapper
            if not self._lock.acquire(timeout=60): return False
            try:
                with sync_playwright() as p:
                    browser = self._get_browser_context(p)
                    page = browser.new_page()
                    return self.engage_post(tweet_id, text, like=like, page=page)
            finally:
                self._lock.release()

        try:
            # Navigate if needed
            if tweet_id not in page.url:
                url = f"https://twitter.com/i/web/status/{tweet_id}"
                page.goto(url)
                page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)

            # 1. Like
            if like:
                try:
                    if page.query_selector('button[data-testid="unlike"]'):
                        print(f"  Tweet {tweet_id} is already liked.")
                    else:
                        like_button = page.wait_for_selector('button[data-testid="like"]', timeout=5000)
                        if like_button:
                            like_button.scroll_into_view_if_needed()
                            like_button.click()
                            print(f"  Clicked Like on {tweet_id}")
                            time.sleep(1)
                except Exception as e:
                    print(f"  Like failed in engage_post: {e}")

            # 2. Comment
            return self.comment_post(tweet_id, text, page=page)

        except Exception as e:
            print(f"Engage Post Error: {e}")
            return False

    def like_post(self, tweet_id: str, page: Page = None) -> bool:
        """
        Likes a tweet. If page is provided, uses existing session.
        """
        should_close = False
        if page is None:
            # Standalone mode (original behavior)
            if not self._lock.acquire(timeout=60): return False
            should_close = True
            # ... (Launch browser logic would go here, omitted for brevity as we focus on batch)
            # For now, let's assume batch mode is the primary user. 
            # If standalone is needed, we need to replicate the launch logic.
            # Re-implementing strictly for completeness:
            try:
                with sync_playwright() as p:
                    browser = self._get_browser_context(p)
                    page = browser.new_page()
                    return self.like_post(tweet_id, page=page)
            finally:
                self._lock.release()

        # Actual Logic with 'page'
        try:
            # Assume we are on the page or need to navigate?
            # If calling from batch, we are already ON the page usually.
            # But let's verify URL.
            if tweet_id not in page.url:
                url = f"https://twitter.com/i/web/status/{tweet_id}"
                print(f"  Navigating to {url} for Like...")
                page.goto(url)
                try:
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
                except:
                    return False

            try:
                if page.query_selector('button[data-testid="unlike"]'):
                    print(f"  Tweet {tweet_id} is already liked.")
                    return True
                    
                like_button = page.wait_for_selector('button[data-testid="like"]', timeout=5000)
                if like_button:
                    like_button.scroll_into_view_if_needed()
                    like_button.click()
                    print(f"  Clicked Like on {tweet_id}")
                    time.sleep(1)
                    return True
            except Exception as e:
                print(f"  Like failed: {e}")
                return False
                
        except Exception as e:
            print(f"Like Error: {e}")
            return False

    def comment_post(self, tweet_id: str, text: str, page: Page = None) -> bool:
        """
        Replies to a tweet.
        """
        if page is None:
            # Standalone wrapper
            if not self._lock.acquire(timeout=60): return False
            try:
                with sync_playwright() as p:
                    browser = self._get_browser_context(p)
                    page = browser.new_page()
                    return self.comment_post(tweet_id, text, page=page)
            finally:
                self._lock.release()

        try:
            # Navigate if needed
            if tweet_id not in page.url:
                url = f"https://twitter.com/i/web/status/{tweet_id}"
                page.goto(url)
                page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)

            try:
                # Try clicking the reply div first to focus
                placeholder = page.query_selector('div[data-testid="tweetTextarea_0_label"]')
                if placeholder: placeholder.click()
                    
                editor = page.wait_for_selector('div.public-DraftEditor-content', timeout=5000)
                
                if editor:
                    editor.click()
                    page.keyboard.type(text, delay=50) 
                    time.sleep(1)
                    
                    submit_btn = page.wait_for_selector('button[data-testid="tweetButtonInline"]', timeout=5000)
                    if submit_btn:
                        if submit_btn.is_disabled():
                            print("  Reply button disabled.")
                        else:
                            submit_btn.click()
                            print(f"  Replied to {tweet_id}")
                            time.sleep(3)
                            return True
                else:
                    print("  Could not find reply editor.")
            except Exception as e:
                print(f"  Reply failed: {e}")
            
            return False

        except Exception as e:
            print(f"Reply Error: {e}")
            return False

twitter_scout = TwitterScout()
