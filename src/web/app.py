from fastapi import FastAPI, Request, Form, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import os
import threading
import asyncio
import time
import concurrent.futures

from src.database import init_db, get_db, get_all_interactions, Interaction, save_interaction
from src.agents.reddit_scout import reddit_scout
from src.agents.twitter_scout import twitter_scout
from src.agents.interaction_agent import interaction_agent
from src.utils.browser_setup import setup_twitter_login
from src.agents.semantic_filter import semantic_filter, keyword_prefilter

app = FastAPI(title="VibeBot Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/web/templates")

# Initialize DB on startup
# Automatic Scheduler (Simple Thread for MVP)
def auto_scout_loop():
    """Runs the scout automatically every X minutes."""
    print("Starting Auto-Scout Loop...")
    while True:
        try:
            print("Auto-Scout: Running scheduled Twitter search...")
            # Default query for auto-scout
            keywords = ["build in public", "indie hacker", "saas mvp"]
            
            # We run them sequentially in the background thread, 
            # but triggering run_scout_task will use the parallel executor internally if applicable.
            for kw in keywords:
                run_scout_task(platform="twitter", limit=10, query=kw)
                time.sleep(60) # Sleep 1 min between keywords
            
            # Sleep for 10 minutes before next batch
            print("Auto-Scout: Sleeping for 10 minutes...")
            time.sleep(600) 
            
        except Exception as e:
            print(f"Auto-Scout Error: {e}")
            time.sleep(60) # Sleep a bit on error

@app.on_event("startup")
def on_startup():
    init_db()
    # Start Auto-Scout in a daemon thread
    # Note: In production, use Celery or APScheduler. 
    # For MVP/Demo, a thread is fine.
    scout_thread = threading.Thread(target=auto_scout_loop, daemon=True)
    scout_thread.start()

@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    interactions = get_all_interactions(limit=5)
    # Simple stats
    total_count = db.query(Interaction).count()
    reddit_count = db.query(Interaction).filter(Interaction.platform == "Reddit").count()
    twitter_count = db.query(Interaction).filter(Interaction.platform == "Twitter").count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "interactions": interactions,
        "stats": {
            "total": total_count,
            "reddit": reddit_count,
            "twitter": twitter_count
        }
    })

@app.get("/scout")
def scout_form(request: Request):
    return templates.TemplateResponse("scout.html", {"request": request})

@app.get("/settings")
def settings_page(request: Request):
    # Check for API keys
    twitter_key_present = bool(os.getenv("TWITTER_API_KEY"))
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "twitter_key_present": twitter_key_present
    })

@app.post("/settings/twitter-login")
def trigger_twitter_login(background_tasks: BackgroundTasks):
    """Triggers the manual login script in a background thread (since it blocks)."""
    thread = threading.Thread(target=setup_twitter_login)
    thread.start()
    
    return RedirectResponse(url="/settings?msg=Browser+Launched", status_code=303)

def run_reddit_task(query: str, limit: int):
    """Worker function for Reddit scouting."""
    try:
        print(f"Starting Reddit Scout for query: {query}")
        subs = ["saas", "startups", "sideproject", "buildinpublic", "entrepreneur"]
        # Use query as search term in subreddits
        reddit_scout.fetch_posts(subreddits=subs, search_query=query, limit=limit)
        print("Reddit Scout Finished")
    except Exception as e:
        print(f"Reddit Scout Error: {e}")

def run_twitter_task(query: str, limit: int):
    """Worker function for Twitter scouting."""
    try:
        search_queries = []
        if query.strip().lower() == "auto":
            search_queries = ["build in public", "vibe coding", "indie hacker", "saas mvp", "startup", "side project"]
        else:
            search_queries = [k.strip() for k in query.split(",") if k.strip()]
        
        print(f"Running Twitter Scout for queries: {search_queries}")
        
        total_found = 0
        for q in search_queries:
            print(f"  [Twitter Scout] Searching for: {q}")
            raw_posts = twitter_scout.fetch_posts(keywords=[q], limit=limit)
            total_found += len(raw_posts)
            
            # Apply Filters
            filtered_posts = keyword_prefilter(raw_posts)
            if filtered_posts:
                final_posts = semantic_filter.filter_posts(filtered_posts)
                print(f"  [Filter] {len(raw_posts)} -> {len(filtered_posts)} -> {len(final_posts)} items")
            else:
                print(f"  [Filter] {len(raw_posts)} -> 0 items")
                
            # Small delay between queries
            if len(search_queries) > 1:
                time.sleep(5)

        # If no posts found on Twitter, log a System Alert
        if total_found == 0:
            print("No posts found on Twitter. Creating System Alert.")
            try:
                save_interaction(
                    platform="System",
                    external_post_id=f"sys_alert_{int(time.time())}",
                    post_content="**Scout Mission Failed**: No posts were found on Twitter/X. \n\nPossible causes:\n1. Not logged in (Twitter requires login to search).\n2. Rate limiting active.\n3. No matches for keywords.\n\nPlease check the terminal for details or use Settings > Login.",
                    status="ERROR",
                    author_name="System Alert",
                    author_handle="@vibebot",
                    metrics={"error": 1}
                )
            except Exception as e:
                print(f"Failed to save system alert: {e}")
                
        print("Twitter Scout Finished")
    except Exception as e:
        print(f"Twitter Scout Error: {e}")

def run_scout_task(platform: str, limit: int, query: str = "build in public"):
    """Background task to run scouting in parallel."""
    
    # Use ThreadPoolExecutor to run tasks concurrently
    # Reddit uses PRAW (blocking I/O), Twitter uses Tweepy/Playwright (blocking/sync I/O here)
    # Threads are suitable for I/O bound tasks like this.
    
    print(f"Launching Scout Mission: Platform={platform}, Query={query}, Limit={limit}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        if platform == "reddit" or platform == "all":
            futures.append(executor.submit(run_reddit_task, query, limit))
        
        if platform == "twitter" or platform == "all":
            futures.append(executor.submit(run_twitter_task, query, limit))
        
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
        print("Scout Mission Completed")

@app.post("/scout")
def trigger_scout(
    background_tasks: BackgroundTasks,
    platform: str = Form(...),
    limit: int = Form(20),
    query: str = Form("auto")
):
    background_tasks.add_task(run_scout_task, platform, limit, query)
    return RedirectResponse(url="/interactions", status_code=303)

@app.get("/interactions")
def list_interactions(request: Request, platform: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Interaction).order_by(Interaction.created_at.desc())
    
    if platform:
        query = query.filter(Interaction.platform == platform)
        
    interactions = query.limit(50).all()
    
    return templates.TemplateResponse("interactions.html", {
        "request": request, 
        "interactions": interactions,
        "current_filter": platform
    })

@app.post("/interactions/{interaction_id}/like")
def like_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if interaction:
        success = False
        if interaction.platform == "Reddit":
            success = reddit_scout.like_post(interaction.external_post_id)
        elif interaction.platform == "Twitter":
            success = twitter_scout.like_post(interaction.external_post_id)
        
        if success:
            pass
            
    return RedirectResponse(url="/interactions", status_code=303)

@app.post("/interactions/{interaction_id}/comment")
def comment_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return RedirectResponse(url="/interactions", status_code=303)

    context_posts = get_all_interactions(limit=10)

    generated_comment = interaction_agent.generate_comment(interaction, context_posts)
    
    if not generated_comment:
        print("Failed to generate comment.")
        return RedirectResponse(url="/interactions", status_code=303)

    print(f"Generated Comment: {generated_comment}")
    
    success = False
    if interaction.platform == "Reddit":
        reddit_scout.like_post(interaction.external_post_id)
        success = reddit_scout.comment_post(interaction.external_post_id, generated_comment)
    elif interaction.platform == "Twitter":
        twitter_scout.like_post(interaction.external_post_id)
        success = twitter_scout.comment_post(interaction.external_post_id, generated_comment)

    if success:
        interaction.bot_comment = generated_comment
        interaction.status = "POSTED"
        db.commit()

    return RedirectResponse(url="/interactions", status_code=303)
