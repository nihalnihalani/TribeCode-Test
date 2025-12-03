# BuildRadar: Product-Grade Plan

## 1. Project Initialization & Setup
- [x] Create/Verify `nihal-branch` and switch to it.
- [x] Create project directory structure (`src/agents`, `src/utils`, `tests`).
- [x] Update `requirements.txt` with web dependencies (`fastapi`, `uvicorn`, `jinja2`, `python-multipart`).
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

## 5. Main Orchestration (Web App - Product Grade)
- [x] **UI/UX Overhaul**:
    - [x] Rename app to **BuildRadar**.
    - [x] Implement a modern sidebar layout with "Blue" theme.
    - [x] Use `icons8` MCP to fetch genuine icons for Sidebar (Dashboard, Scout, Archive, Settings).
    - [x] Redesign `dashboard.html` with charts (Chart.js) and key metrics cards.
    - [x] Redesign `scout.html` to be a "Campaign Launcher" rather than a simple form.
    - [x] Redesign `interactions.html` as a "Feed" with card layout (like Twitter/Reddit style) rather than a table.
- [x] **Functionality Updates**:
    - [x] Update `scout` endpoint to ALWAYS fetch from **BOTH** Reddit and X (parallel execution).
    - [x] Remove the hardcoded "5 limit" default; set default to 20-50 and allow user input up to 100.
    - [x] Enhance `twitter_scout.py` to accept dynamic queries (not just #buildinpublic).
    - [x] Add "Search Query" input field to the Scout UI so users can customize what they are looking for (e.g. "marketing", "AI wrapper").
- [x] **Assets**:
    - [x] Create `src/web/static/css/style.css` for custom product styling.
    - [x] Create `src/web/static/js/main.js` for dynamic interactions (like "Load More").

## 6. Testing
- [x] Update `tests/test_web.py` to reflect new UI structure.
- [x] Verify parallel execution of Reddit/X scouting.

## 7. Product Polish (Post-MVP)
- [ ] **Settings Page**: Implement `/settings` to view/edit configuration (API Keys logic placeholders).
- [ ] **Deployment**: Create `Dockerfile` for containerization.
