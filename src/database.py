import os
from datetime import datetime
from typing import Optional, List
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
    bot_comment = Column(Text, nullable=True)
    status = Column(String, default='ARCHIVED') # 'PLANNED', 'POSTED', 'ARCHIVED'
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Interaction(platform='{self.platform}', id='{self.external_post_id}', status='{self.status}')>"

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

def save_interaction(platform: str, external_post_id: str, post_content: str, status: str = "ARCHIVED", bot_comment: Optional[str] = None):
    """Saves a new interaction to the database."""
    session = SessionLocal()
    try:
        # Check if already exists to avoid UniqueConstraintError, though check_deduplication should be used first.
        existing = session.query(Interaction).filter_by(external_post_id=external_post_id).first()
        if existing:
            # Update if exists? Or just return? For now, we update fields if it exists, or skip.
            # Let's treat it as an update/upsert if it exists, or just skip if immutable.
            # The prompt says "Archive with local db", so let's ensure it's saved.
            print(f"Interaction {external_post_id} already exists. Skipping creation.")
            return existing
        
        new_interaction = Interaction(
            platform=platform,
            external_post_id=external_post_id,
            post_content=post_content,
            bot_comment=bot_comment,
            status=status
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

