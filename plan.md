# VibeBot MVP Plan (Web App Version)

## 1. Project Initialization & Setup
- [x] Create/Verify `nihal-branch` and switch to it.
- [x] Create project directory structure (`src/agents`, `src/utils`, `tests`).
- [ ] Update `requirements.txt` with web dependencies (`fastapi`, `uvicorn`, `jinja2`, `python-multipart`).
- [x] Create `.env.example` template.

## 2. Database & Persistence (The Archivist)
- [x] Implement `src/database.py` to handle SQLite connection.
- [x] Create `interactions` table schema as per README.
- [x] Implement helper functions: `save_interaction`, `check_deduplication`, `get_all_interactions`.

## 3. Reddit Integration (The Scout - Phase 1)
- [x] Implement `src/agents/reddit_scout.py`.
- [x] Add PRAW authentication.
- [x] Implement `fetch_posts(subreddits, limit)` to search for keywords (e.g., "build in public").
- [x] Implement `like_post(post_id)` functionality.
- [x] Integrate with Archivist to save fetched posts to DB.

## 4. X (Twitter) Integration (The Scout - Phase 2)
- [x] Implement `src/agents/twitter_scout.py` using `tweepy`.
- [x] **Constraint Note**: Since X Free Tier is Write-Only, we will implement the structure and Authentication check.
- [x] Add placeholder/stub functions for `fetch_posts` and `like_post` that log a "Upgrade Tier" warning, or explore limited scraping if requested (but API is preferred for stability).

## 5. Main Orchestration (Web App)
- [ ] Install `fastapi`, `uvicorn`, `jinja2` (for simple templates).
- [ ] Implement `src/web/app.py`:
    - `GET /`: Dashboard showing archived posts stats.
    - `GET /scout`: Button/Form to trigger scouting (Reddit/X).
    - `POST /scout`: API endpoint that calls `reddit_scout` or `twitter_scout` background tasks.
    - `GET /interactions`: Table view of archived posts.
    - `POST /interactions/{id}/like`: Action to trigger "Like".
- [ ] Create templates in `src/web/templates/` (Dashboard, List View).

## 6. Testing
- [ ] Create `tests/test_db.py` to verify storage.
- [ ] Create `tests/test_reddit.py` with mocks.
- [ ] Create `tests/test_web.py` to test API endpoints.

