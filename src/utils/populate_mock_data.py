import sys
import os
sys.path.insert(0, os.getcwd())

from src.database import init_db, save_interaction

def populate_mock_data():
    print("Populating DB with realistic 'Vibe Coding' mock data...")
    init_db()
    
    mock_posts = [
        {
            "id": "1730000000001",
            "text": "Just shipped the new MVP for my vibe coding agent! 🚀 Using Playwright + Claude to automate everything. The future of coding is just vibing with your AI pair programmer. #buildinpublic #vibeCoding",
            "author_name": "Alex Builder",
            "author_handle": "@alexbuilds",
            "post_url": "https://twitter.com/alexbuilds/status/1730000000001",
            "metrics": {"replies": "12", "retweets": "5", "likes": "89"},
            "media_url": "https://pbs.twimg.com/media/GA_example1.jpg" # Dummy, but UI will handle broken image gracefully or show icon
        },
        {
            "id": "1730000000002",
            "text": "Spending my Saturday night refactoring the backend. Vibe coding playlist on, coffee in hand. Who else is grinding? 💻☕️ #indiehacker #startup",
            "author_name": "Sarah Codes",
            "author_handle": "@sarah_dev",
            "post_url": "https://twitter.com/sarah_dev/status/1730000000002",
            "metrics": {"replies": "34", "retweets": "12", "likes": "245"},
            "media_url": None
        },
        {
            "id": "1730000000003",
            "text": "The best part of #vibeCoding is when you write one line of code and the AI writes the next 20. Pure flow state. 🌊 #AI #coding",
            "author_name": "DevFlow",
            "author_handle": "@dev_flow_state",
            "post_url": "https://twitter.com/dev_flow_state/status/1730000000003",
            "metrics": {"replies": "8", "retweets": "2", "likes": "56"},
            "media_url": None
        }
    ]
    
    for post in mock_posts:
        save_interaction(
            platform="Twitter",
            external_post_id=post["id"],
            post_content=post["text"],
            status="ARCHIVED",
            author_name=post["author_name"],
            author_handle=post["author_handle"],
            post_url=post["post_url"],
            metrics=post["metrics"],
            media_url=post["media_url"]
        )
        print(f"Saved mock post: {post['id']}")

if __name__ == "__main__":
    populate_mock_data()

