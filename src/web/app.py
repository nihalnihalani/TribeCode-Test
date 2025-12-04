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
    twitter_count = db.query(Interaction).filter(Interaction.platform == "Twitter").count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "interactions": interactions,
        "stats": {
            "total": total_count,
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

def run_twitter_task(query: str, limit: int, auto_like: bool = False, auto_comment: bool = False):
    """Worker function for Twitter scouting."""
    try:
        search_queries = []
        if query.strip().lower() == "auto":
            search_queries = ["build in public", "vibe coding", "indie hacker", "saas mvp", "startup", "side project"]
        else:
            search_queries = [k.strip() for k in query.split(",") if k.strip()]
        
        print(f"Running Twitter Scout for queries: {search_queries} (Auto-Like={auto_like}, Auto-Comment={auto_comment})")
        
        total_found = 0
        
        # If Auto-Engage is ON, we use the batch_engage method which handles everything in one session
        if auto_like or auto_comment:
            # Determine tag for batch
            batch_tag = search_queries[0] if len(search_queries) == 1 else "Auto-Pilot"
            if query.strip().lower() != "auto" and len(search_queries) > 1:
                batch_tag = "Custom Mix"

            processed = twitter_scout.batch_engage(
                keywords=search_queries,
                limit=limit,
                auto_like=auto_like,
                auto_comment=auto_comment,
                interaction_agent=interaction_agent,
                tag=batch_tag
            )
            total_found = processed
            print(f"Batch Engage Completed. Processed {processed} tweets.")
            
        else:
            # Standard Discovery Mode (Fetch only)
            for q in search_queries:
                print(f"  [Twitter Scout] Searching for: {q}")
                raw_posts = twitter_scout.fetch_posts(keywords=[q], limit=limit, tag=q)
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

def run_scout_task(platform: str, limit: int, query: str = "build in public", auto_like: bool = False, auto_comment: bool = False):
    """Background task to run scouting in parallel."""
    
    # Use ThreadPoolExecutor to run tasks concurrently
    # Twitter uses Tweepy/Playwright (blocking/sync I/O here)
    # Threads are suitable for I/O bound tasks like this.
    
    print(f"Launching Scout Mission: Platform={platform}, Query={query}, Limit={limit}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        # Always default to Twitter since Reddit is removed
        futures.append(executor.submit(run_twitter_task, query, limit, auto_like, auto_comment))
        
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
        print("Scout Mission Completed")

@app.post("/scout")
def trigger_scout(
    background_tasks: BackgroundTasks,
    platform: str = Form(...),
    limit: int = Form(20),
    query: str = Form("auto"),
    auto_like: bool = Form(False),
    auto_comment: bool = Form(False)
):
    background_tasks.add_task(run_scout_task, platform, limit, query, auto_like, auto_comment)
    return RedirectResponse(url="/interactions", status_code=303)

@app.post("/interactions/clear")
def clear_interactions(db: Session = Depends(get_db)):
    """Clears all interactions from the database."""
    try:
        # Delete all rows
        db.query(Interaction).delete()
        db.commit()
        print("Database cleared.")
    except Exception as e:
        print(f"Error clearing database: {e}")
        db.rollback()
        
    return RedirectResponse(url="/interactions", status_code=303)

@app.get("/interactions")
def list_interactions(request: Request, platform: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Interaction).order_by(Interaction.created_at.desc())
    
    if platform:
        query = query.filter(Interaction.platform == platform)
        
    interactions = query.limit(100).all()
    
    # Group by tag
    grouped_interactions = {}
    for i in interactions:
        tag = i.tag if i.tag else "Uncategorized"
        if tag not in grouped_interactions:
            grouped_interactions[tag] = []
        grouped_interactions[tag].append(i)
        
    # Sort groups? Maybe by most recent post in group?
    # For now, just pass the dict.
    
    return templates.TemplateResponse("interactions.html", {
        "request": request, 
        "grouped_interactions": grouped_interactions,
        "interactions": interactions, # Keep flat list if needed for fallback
        "current_filter": platform
    })

@app.post("/interactions/{interaction_id}/like")
def like_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if interaction:
        success = False
        if interaction.platform == "Twitter":
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
    if interaction.platform == "Twitter":
        # Use the new atomic engage_post method to Like AND Comment in one session
        success = twitter_scout.engage_post(interaction.external_post_id, generated_comment, like=True)

    if success:
        interaction.bot_comment = generated_comment
        interaction.status = "POSTED"
        db.commit()

    return RedirectResponse(url="/interactions", status_code=303)
