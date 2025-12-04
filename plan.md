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

## 3. X (Twitter) Integration (The Scout)
- [x] Implement `src/agents/twitter_scout.py` using `tweepy` and `playwright`.
- [x] Implement `fetch_posts` using browser automation.
- [x] Implement `like_post` and `comment_post` using browser automation.
- [x] Integrate with Archivist to save fetched posts to DB.

## 4. Main Orchestration (Web App - Product Grade)
- [x] **UI/UX Overhaul**:
    - [x] Rename app to **BuildRadar**.
    - [x] Implement a modern sidebar layout with "Blue" theme.
    - [x] Use `icons8` MCP to fetch genuine icons for Sidebar (Dashboard, Scout, Archive, Settings).
    - [x] Redesign `dashboard.html` with charts (Chart.js) and key metrics cards.
    - [x] Redesign `scout.html` to be a "Campaign Launcher".
    - [x] Redesign `interactions.html` as a "Feed" with card layout.
- [x] **Functionality Updates**:
    - [x] Focus strictly on Twitter (Reddit removed).
    - [x] Remove the hardcoded "5 limit" default; set default to 20-50.
    - [x] Enhance `twitter_scout.py` to accept dynamic queries.
    - [x] Add "Search Query" input field to the Scout UI.
- [x] **Assets**:
    - [x] Create `src/web/static/css/style.css` for custom product styling.
    - [x] Create `src/web/static/js/main.js` for dynamic interactions.

## 5. Testing
- [x] Update `tests/test_web.py` to reflect new UI structure.
- [x] Verify Twitter scouting.

## 6. Product Polish (Post-MVP)
- [ ] **Settings Page**: Implement `/settings` to view/edit configuration.
- [ ] **Deployment**: Create `Dockerfile` for containerization.
