from fastapi import FastAPI, Request, Form, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import os

from src.database import init_db, get_db, get_all_interactions, Interaction, save_interaction
from src.agents.reddit_scout import reddit_scout
from src.agents.twitter_scout import twitter_scout
from src.agents.interaction_agent import interaction_agent
from src.utils.browser_setup import setup_twitter_login
from src.agents.semantic_filter import semantic_filter, keyword_prefilter
import threading
import asyncio
import time

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
            
            # We run them sequentially
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
    return templates.TemplateResponse("settings.html", {"request": request})

@app.post("/settings/twitter-login")
def trigger_twitter_login(background_tasks: BackgroundTasks):
    """Triggers the manual login script in a background thread (since it blocks)."""
    # Using threading.Thread because background_tasks might not be enough if FastAPI manages the event loop in a way that playwright sync api dislikes.
    # But let's try BackgroundTasks first or just spawn a thread.
    # setup_twitter_login() blocks until browser close.
    
    thread = threading.Thread(target=setup_twitter_login)
    thread.start()
    
    return RedirectResponse(url="/settings?msg=Browser+Launched", status_code=303)

def run_scout_task(platform: str, limit: int, query: str = "build in public"):
    """Background task to run scouting."""
    # Parallel execution if 'all' is selected, or specific platform
    # Since this is a background task, simple sequential execution is fine for now, 
    # but we ensure both run if 'all' is selected.
    
    if platform == "reddit" or platform == "all":
        # We assume the query can be used as search term. 
        # For subreddits, we might keep the default list but filter by query, 
        # OR search GLOBALLY on Reddit with that query?
        # Let's keep the specific subreddits for high signal-to-noise, 
        # but use the user's query as the search term WITHIN those subs.
        subs = ["saas", "startups", "sideproject", "buildinpublic", "entrepreneur"]
        reddit_scout.fetch_posts(subreddits=subs, search_query=query, limit=limit)
    
    if platform == "twitter" or platform == "all":
        # Pass the query to Twitter Scout
        print(f"Running Twitter Scout for query: {query}")
        raw_posts = twitter_scout.fetch_posts(keywords=[query], limit=limit)
        
        # Apply Filters
        # 1. Keyword Prefilter (Fast)
        # Note: Twitter search already does keyword matching, but we can filter out "hiring" etc.
        filtered_posts = keyword_prefilter(raw_posts)
        print(f"  [Filter] {len(raw_posts)} -> {len(filtered_posts)} after keyword filter")
        
        # 2. Semantic Filter (Smart)
        # Only apply if we have posts left
        if filtered_posts:
            final_posts = semantic_filter.filter_posts(filtered_posts)
            print(f"  [Filter] {len(filtered_posts)} -> {len(final_posts)} after semantic filter")
        else:
            final_posts = []
            
        # Note: twitter_scout.fetch_posts ALREADY saves to DB with ARCHIVED status.
        # We might want to update their status to 'QUALIFIED' if they pass filters?
        # Or just rely on the fetch to save everything and we filter on display?
        # For "Automatic", we probably want to know which ones are "Good".
        # Let's update the status in DB for the ones that passed.
        
        for post in final_posts:
            # We need to update the interaction in DB
            # This requires a DB session. 
            # Ideally fetch_posts returns objects we can update, or we do a quick update query.
            pass # For now, we just trust the Scout archived them.

@app.post("/scout")
def trigger_scout(
    background_tasks: BackgroundTasks,
    platform: str = Form(...),
    limit: int = Form(20),
    query: str = Form("build in public")
):
    background_tasks.add_task(run_scout_task, platform, limit, query)
    return RedirectResponse(url="/interactions", status_code=303)

@app.get("/interactions")
def list_interactions(request: Request, db: Session = Depends(get_db)):
    # Fetch all interactions (or implement pagination later)
    interactions = get_all_interactions(limit=50) 
    return templates.TemplateResponse("interactions.html", {
        "request": request, 
        "interactions": interactions
    })

@app.post("/interactions/{interaction_id}/like")
def like_interaction(interaction_id: int, db: Session = Depends(get_db)):
    # Get interaction to find external ID and platform
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if interaction:
        success = False
        if interaction.platform == "Reddit":
            success = reddit_scout.like_post(interaction.external_post_id)
        elif interaction.platform == "Twitter":
            success = twitter_scout.like_post(interaction.external_post_id)
        
        if success:
            # Update status in DB? 
            # For now just logging, maybe update status to 'LIKED' if we had that status
            pass
            
    return RedirectResponse(url="/interactions", status_code=303)

@app.post("/interactions/{interaction_id}/comment")
def comment_interaction(interaction_id: int, db: Session = Depends(get_db)):
    # 1. Fetch target interaction
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        return RedirectResponse(url="/interactions", status_code=303)

    # 2. Fetch context (recent interactions)
    context_posts = get_all_interactions(limit=10)

    # 3. Generate Comment
    generated_comment = interaction_agent.generate_comment(interaction, context_posts)
    
    if not generated_comment:
        print("Failed to generate comment.")
        return RedirectResponse(url="/interactions", status_code=303)

    print(f"Generated Comment: {generated_comment}")
    
    # 4. Post Comment & Like
    success = False
    if interaction.platform == "Reddit":
        # Like first
        reddit_scout.like_post(interaction.external_post_id)
        # Then comment
        success = reddit_scout.comment_post(interaction.external_post_id, generated_comment)
    elif interaction.platform == "Twitter":
        twitter_scout.like_post(interaction.external_post_id)
        success = twitter_scout.comment_post(interaction.external_post_id, generated_comment)

    # 5. Update DB
    if success:
        interaction.bot_comment = generated_comment
        interaction.status = "POSTED"
        db.commit()

    return RedirectResponse(url="/interactions", status_code=303)
