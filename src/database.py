import os
from datetime import datetime
from typing import Optional, List, Dict
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Use a default if not in env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vibebot.db")

Base = declarative_base()

class Interaction(Base):
    __tablename__ = 'interactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String, nullable=False)  # 'Reddit', 'Twitter', etc.
    external_post_id = Column(String, unique=True, nullable=False)
    post_content = Column(Text, nullable=True)
    
    # New Fields for "All Details"
    author_name = Column(String, nullable=True)
    author_handle = Column(String, nullable=True)
    post_url = Column(String, nullable=True)
    metrics_json = Column(Text, nullable=True) # JSON string for likes, retweets, etc.
    media_url = Column(String, nullable=True)
    
    bot_comment = Column(Text, nullable=True)
    status = Column(String, default='ARCHIVED') # 'PLANNED', 'POSTED', 'ARCHIVED'
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Interaction(platform='{self.platform}', id='{self.external_post_id}', status='{self.status}')>"
    
    @property
    def metrics(self):
        if self.metrics_json:
            try:
                return json.loads(self.metrics_json)
            except:
                return {}
        return {}

# Setup Engine and Session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Creates the database tables."""
    Base.metadata.create_all(engine)

def get_db():
    """Dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Archivist Helper Functions ---

def save_interaction(
    platform: str, 
    external_post_id: str, 
    post_content: str, 
    status: str = "ARCHIVED", 
    bot_comment: Optional[str] = None,
    author_name: Optional[str] = None,
    author_handle: Optional[str] = None,
    post_url: Optional[str] = None,
    metrics: Optional[Dict] = None,
    media_url: Optional[str] = None
):
    """Saves a new interaction to the database."""
    session = SessionLocal()
    try:
        existing = session.query(Interaction).filter_by(external_post_id=external_post_id).first()
        
        metrics_str = json.dumps(metrics) if metrics else None
        
        if existing:
            print(f"Interaction {external_post_id} already exists. Updating.")
            # Update fields if they are provided (enrichment)
            if author_name: existing.author_name = author_name
            if author_handle: existing.author_handle = author_handle
            if post_url: existing.post_url = post_url
            if metrics_str: existing.metrics_json = metrics_str
            if media_url: existing.media_url = media_url
            
            session.commit()
            return existing
        
        new_interaction = Interaction(
            platform=platform,
            external_post_id=external_post_id,
            post_content=post_content,
            bot_comment=bot_comment,
            status=status,
            author_name=author_name,
            author_handle=author_handle,
            post_url=post_url,
            metrics_json=metrics_str,
            media_url=media_url
        )
        session.add(new_interaction)
        session.commit()
        session.refresh(new_interaction)
        return new_interaction
    except Exception as e:
        session.rollback()
        print(f"Error saving interaction: {e}")
        raise
    finally:
        session.close()

def check_deduplication(external_post_id: str) -> bool:
    """Returns True if the post has already been processed/archived."""
    session = SessionLocal()
    try:
        exists = session.query(Interaction).filter_by(external_post_id=external_post_id).first()
        return exists is not None
    finally:
        session.close()

def get_all_interactions(limit: int = 100) -> List[Interaction]:
    """Retrieves recent interactions."""
    session = SessionLocal()
    try:
        return session.query(Interaction).order_by(Interaction.created_at.desc()).limit(limit).all()
    finally:
        session.close()
