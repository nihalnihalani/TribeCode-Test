# VibeBot: Autonomous Build-in-Public Engagement Agent

VibeBot is an autonomous agent designed to identify, analyze, and engage with "Build in Public" and "Vibe Coding" content on X (Twitter). Unlike simple automation scripts, this system is built with a production-first mindset, featuring comprehensive unit testing, modular agentic architecture, and local archival persistence.

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=37410&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=37410&format=png&size=24" height="24"/></picture> Project Overview

The "Build in Public" movement on X has created a high-velocity stream of content. Developers are shipping MVPs daily, but finding genuine signals amidst the noise is difficult. VibeBot solves this by:
1.  **Scouting** X for high-signal keywords (e.g., "build in public", "vibe coding").
2.  **Filtering** noise using heuristic and semantic analysis.
3.  **Engaging** authentically using LLMs (Claude 3.5 Sonnet).
4.  **Archiving** interactions for long-term analysis.

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=6Fsj3rv2DCmG&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=6Fsj3rv2DCmG&format=png&size=24" height="24"/></picture> Key Features

### 1. The Scout (Discovery Agent)
<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=10601&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=10601&format=png&size=24" height="24"/></picture> **Radar & Search**
- **Autonomous Browsing**: Uses Playwright to navigate X safely and effectively.
- **Smart Queries**: targeted searches for keywords like `#buildinpublic`, `indie hacker`, and `saas mvp`.
- **Rate Limiting**: Hard-coded sleeps and human-like browsing patterns to ensure account safety.
- **Deduplication**: Never processes the same tweet twice.

### 2. The Vibe Check (Intelligence Agent)
<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=2070&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=2070&format=png&size=24" height="24"/></picture> **Analysis & Engagement**
- **Context Awareness**: Analyzes the tweet's text, author, and metrics.
- **LLM-Powered**: Uses Claude 3.5 Sonnet to generate genuine, non-spammy replies.
- **Safety Rails**: Filters out political, tragic, or unrelated viral content.
- **Personality**: Adopts a "casual developer" persona (lowercase usage, specific technical questions).

### 3. The Archivist (Persistence Layer)
<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=11360&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=11360&format=png&size=24" height="24"/></picture> **Database & Memory**
- **Local Storage**: SQLite database stores every interaction, tweet, and generated reply.
- **Audit Trail**: Keeps track of status (`ARCHIVED`, `PLANNED`, `POSTED`).
- **Metrics Tracking**: Stores like/retweet/reply counts at the time of capture.

### 4. Human-in-the-Loop Dashboard
<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=aVHe2jHuORcA&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=aVHe2jHuORcA&format=png&size=24" height="24"/></picture> **Control Center**
- **Web UI**: A clean, modern dashboard built with FastAPI and Jinja2.
- **Feed View**: Review captured tweets in a card-based layout.
- **Manual Overrides**: Manually trigger "Like" or "Reply" actions from the UI.
- **Campaigns**: Launch specific scouting missions with custom keywords.

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=11240&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=11240&format=png&size=24" height="24"/></picture> Tech Stack

- **Core**: Python 3.11+
- **Browser Automation**: Playwright (for X interaction)
- **Web Framework**: FastAPI + Jinja2 (Dashboard)
- **Database**: SQLite + SQLAlchemy
- **AI/LLM**: Anthropic Claude 3.5 Sonnet
- **Testing**: pytest

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=2177&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=2177&format=png&size=24" height="24"/></picture> Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/vibebot.git
cd vibebot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Environment Setup
Create a `.env` file with your API keys:

```ini
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///vibebot.db
# Optional: Twitter credentials if we move to API later, 
# currently uses browser profile in 'twitter_auth_data'
```

### 4. Authentication (Browser Profile)
VibeBot uses a persistent browser profile to avoid constant logins.
Run the login helper to set up your session:

```bash
python -c "from src.utils.browser_setup import setup_twitter_login; setup_twitter_login()"
```
*This will open a browser window. Log in to X manually, then close the browser. Your session cookies will be saved.*

### 5. Run the Agent
Start the web dashboard and the auto-scout background process:

```bash
python main.py
```
Visit `http://localhost:8000` to see the dashboard.

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=111782&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=111782&format=png&size=24" height="24"/></picture> Testing

We enforce strict TDD. Run tests before making changes.

```bash
# Run all tests
pytest -v

# Run specific agent tests
pytest tests/test_agents.py
```

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=876&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=876&format=png&size=24" height="24"/></picture> Ethics & Safety

- **No Spam**: The bot is designed to add value, not noise.
- **Transparency**: The User-Agent allows platforms to identify the traffic.
- **Rate Limits**: We respect the implicit rate limits of the web platform to avoid burdening servers.
- **Content Safety**: We do not engage with harmful or controversial content.
