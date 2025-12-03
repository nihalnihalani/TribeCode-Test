import os
from playwright.sync_api import sync_playwright

def setup_twitter_login():
    """
    Launches a browser with a persistent context to allow the user to log in to Twitter.
    The session will be saved to 'twitter_auth_data' directory.
    """
    # Ensure the directory exists or let Playwright create it
    user_data_dir = os.path.join(os.getcwd(), "twitter_auth_data")
    
    print(f"Launching browser with user data dir: {user_data_dir}")
    print("Please log in to Twitter in the opened window.")
    print("Close the browser window when you are done.")

    with sync_playwright() as p:
        # specific args to avoid detection/issues
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 720},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.new_page()
        page.goto("https://twitter.com/login")
        
        # Keep the script running until the user closes the browser
        # We can monitor if the browser context is closed
        try:
            page.wait_for_timeout(300000) # Wait 5 minutes or untill closed
        except Exception as e:
            print(f"Browser closed or error: {e}")
        finally:
            browser.close()
            print("Browser closed. Session data saved.")

if __name__ == "__main__":
    setup_twitter_login()

