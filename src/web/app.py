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

app = FastAPI(title="VibeBot Dashboard")

# Templates
templates = Jinja2Templates(directory="src/web/templates")

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

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

def run_scout_task(platform: str, limit: int):
    """Background task to run scouting."""
    if platform == "reddit" or platform == "all":
        subs = ["saas", "startups", "sideproject", "buildinpublic"]
        reddit_scout.fetch_posts(subreddits=subs, limit=limit)
    
    if platform == "twitter" or platform == "all":
        twitter_scout.fetch_posts(keywords=["#buildinpublic", "saas"], limit=limit)

@app.post("/scout")
def trigger_scout(
    background_tasks: BackgroundTasks,
    platform: str = Form(...),
    limit: int = Form(5)
):
    background_tasks.add_task(run_scout_task, platform, limit)
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

