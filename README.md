# VibeBot: Autonomous Build-in-Public Engagement Agent

VibeBot is an autonomous agent designed to identify, analyze, and engage with "Vibe Coding" and "Build in Public" content across Reddit and LinkedIn. Unlike simple automation scripts, this system is built with a production-first mindset, featuring comprehensive unit testing, modular agentic architecture, and local archival persistence.

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=2754&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=2754&format=png&size=24" height="24"/></picture> Problem Statement

**The Context** The "Build in Public" movement has created a high-value stream of content across fragmented platforms. Developers are constantly shipping MVPs, but finding these genuine signals amidst the noise is difficult.

### The Pain Points

- **High Noise-to-Signal Ratio**: Manually filtering for "vibe coding" posts is inefficient.
- **Inconsistent Engagement**: Sustaining supportive interaction (liking/commenting) manually leads to burnout.
- **Data Ephemerality**: Valuable interactions are lost to the feed with no central archive.

### The Solution
An agentic system that **Detects** relevance, **Engages** intelligently using LLMs, and **Archives** interactions to a local SQLite database for future analysis.

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=60641&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=60641&format=png&size=24" height="24"/></picture> System Architecture

The project follows a Multi-Agent approach (refer to docs/Agents+Skills.md for deep dive):

1. **The Scout (Discovery Agent)**
   - **Role**: Scrapes and fetches posts from targeted subreddits and LinkedIn hashtags.
   - **Skills**: `fetch_reddit_feed`, `search_linkedin`, `heuristic_filter`.
   - **Unit Tests**: Mocks API responses to ensure rate limits are respected and filters work correctly.

2. **The Vibe Check (Engagement Agent)**
   - **Role**: Analyzes post content and generates context-aware comments.
   - **Skills**: `analyze_sentiment`, `generate_response` (LLM), `safety_check`.
   - **Unit Tests**: Validates that generated comments are positive, non-spammy, and within character limits.

3. **The Archivist (Persistence Agent)**
   - **Role**: Manages the local database state.
   - **Skills**: `check_deduplication`, `commit_transaction`, `export_logs`.
   - **Unit Tests**: Ensures idempotency (never commenting on the same post twice).

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=24551&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=24551&format=png&size=24" height="24"/></picture> Tech Stack

- **Core**: Python 3.11+
- **Orchestration**: LangChain / Pydantic AI (or your preferred framework)
- **Database**: SQLite (local persistence)
- **Testing**: pytest + unittest.mock
- **APIs**: PRAW (Reddit), LinkedIn API, OpenAI/Anthropic (Generation)

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=QQwcfqZkWqUL&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=QQwcfqZkWqUL&format=png&size=24" height="24"/></picture> Testing Strategy (Priority #1)

We enforce a strict TDD (Test Driven Development) approach. No feature is merged without accompanying tests.

### Running Tests

```bash
# Run all tests with verbose output
pytest -v

# Run only the agent logic tests
pytest tests/test_agents.py
```

### Key Test Suites

- `tests/test_discovery.py`: Mocks JSON responses to verify filtering logic.
- `tests/test_safety.py`: adversarial testing against the LLM prompt to prevent toxic output.
- `tests/test_db.py`: Verifies schema integrity and deduplication logic.

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=11360&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=11360&format=png&size=24" height="24"/></picture> Data Schema (Local DB)

We use a lightweight interactions table to archive all activity.

```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,      -- 'Reddit' or 'LinkedIn'
    external_post_id TEXT UNIQUE,-- The platform's native ID
    post_content TEXT,           -- The user's original post
    bot_comment TEXT,            -- What we replied
    status TEXT,                 -- 'PLANNED', 'POSTED', 'ARCHIVED'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=92053&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=92053&format=png&size=24" height="24"/></picture> Getting Started

### Clone the Repo

```bash
git clone https://github.com/yourusername/vibebot.git
cd vibebot
```

### Environment Variables
Create a `.env` file based on `.env.example`:

```ini
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
OPENAI_API_KEY=...
DATABASE_URL=sqlite:///vibebot.db
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Scout

```bash
python main.py --mode=scout
```

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=876&format=png&size=24&color=ffffff"><img src="https://img.icons8.com/?id=876&format=png&size=24" height="24"/></picture> Ethics & Safety

This bot is designed to be supportive, not spammy.

- **Rate Limits**: The bot is hard-coded to sleep between actions to mimic human behavior.
- **Disclosure**: The User-Agent string identifies this as a bot.
- **Content Policy**: The `safety_check` skill explicitly rejects posts about politics, tragedy, or unrelated viral content.
