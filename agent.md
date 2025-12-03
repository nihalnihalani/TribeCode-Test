# Agent Rules and Guidelines

## User Rules
- **Git Workflow**: Every time substantial changes are made, they must be pushed to the GitHub repository in the branch `nihal-branch` (or "nihal's branch") with proper comments. If the branch is not present, it must be created.
- **Mock Data Usage**: Mock data is ONLY used to test the application (e.g. in `tests/`), NOT for the actual working of the application. Production code must rely on real data and integrations.

## General Agent Guidelines

### Tool Usage
- **Natural Language**: Do not refer to tool names explicitly; describe actions in natural language.
- **Specialized Tools**: Use specialized tools (e.g., `read_file`, `write_file`) instead of terminal commands (`cat`, `echo`).
- **Parallelism**: Maximize parallel tool calls for independent operations.

### Code Editing & Exploration
- **Semantic Search**: Start with broad queries (`codebase_search`) and narrow down. Run multiple searches with different wordings.
- **Context**: Trace symbols to definitions/usages. Understand the "full picture" before editing.
- **Style & Conventions**: Check existing patterns/helpers before implementing new logic. Match existing coding style.
- **Linter Errors**: Fix introduced linter errors immediately.
- **No Reverts**: Do not revert changes unless explicitly asked.
- **Real Data Only**: Never use dummy, demo, or mock data in production code. All implementations must work with real APIs, real databases, and real integrations. Mock data should only exist in test files (e.g., `tests/` directory) for unit testing purposes. Production code must handle real data sources and edge cases properly.

## Browser & Testing Guidelines

### Testing Flow
1.  **Navigate**: Go to the page to test.
2.  **Snapshot**: Capture page elements (`browser_snapshot`).
3.  **Interact**: Perform actions (click, type) and observe results.
4.  **Re-snapshot**: Verify changes.
5.  **Visual Inspection**: Use `browser_take_screenshot` for visual checks.

### Restrictions
- **Local Server**: Do not start the local web server unless prompted.
- **Ports**: Do not guess ports; check the codebase.
- **Interaction**: Do not use the shell to interact with the browser; use browser tools.
- **Test Mocks**: Mocking is acceptable and recommended in test files (`tests/`) to isolate unit tests. However, production code (e.g., `src/`) must use real integrations and data sources.

## Code Quality & Best Practices

### Python Standards
- **Type Hints**: Use type hints for function parameters and return types where appropriate.
- **Docstrings**: Add docstrings to all classes and public functions explaining their purpose.
- **Error Handling**: Use specific exception types and provide meaningful error messages.
- **Imports**: Follow PEP 8 import ordering (standard library, third-party, local).
- **Naming**: Use descriptive names following PEP 8 (snake_case for functions/variables, PascalCase for classes).

### Database & Persistence
- **Transactions**: Always use database transactions for multi-step operations.
- **Idempotency**: Ensure all database operations are idempotent (can be safely retried).
- **Migrations**: Document schema changes and provide migration scripts if needed.
- **Connection Management**: Use context managers for database connections when possible.

### API Integration
- **Rate Limiting**: Always respect API rate limits and implement appropriate delays.
- **Error Handling**: Handle API errors gracefully with retries and exponential backoff where appropriate.
- **Authentication**: Never hardcode credentials; use environment variables or secure vaults.
- **User-Agent**: Always identify bots with clear User-Agent strings per platform requirements.

### Agent Architecture
- **Modularity**: Keep agents separate and focused on single responsibilities.
- **State Management**: Use the database for state persistence, not in-memory storage.
- **Context Awareness**: Agents should have access to historical context when making decisions.
- **Safety Checks**: Implement content filtering and safety checks before posting.

### Response Format
- **Concise but Thorough**: Provide complete information without unnecessary verbosity.
- **Format Complex Data**: Use markdown for structured data presentation.
- **Explain Actions**: Clearly explain what actions were taken and why.

## File & Project Structure

### Directory Organization
- **Source Code**: All production code lives in `src/` directory.
- **Tests**: All test files live in `tests/` directory with `test_` prefix.
- **Templates**: Web templates are in `src/web/templates/`.
- **Static Assets**: CSS, JS, and images in `src/web/static/`.
- **Database**: SQLite database file (`vibebot.db`) should be in project root or configurable via environment.

### File Naming
- **Python Files**: Use `snake_case.py` for modules.
- **Test Files**: Use `test_<module_name>.py` pattern.
- **Configuration**: Use `.env` for environment variables, never commit actual secrets.

## Environment & Dependencies

### Environment Variables
- **Required Variables**: Check `.env.example` for required environment variables.
- **Validation**: Validate required environment variables on application startup.
- **Defaults**: Provide sensible defaults where possible, but fail fast if critical variables are missing.

### Dependencies
- **Version Pinning**: Pin dependency versions in `requirements.txt` for reproducibility.
- **Security**: Regularly update dependencies to patch security vulnerabilities.
- **Minimal Dependencies**: Only include necessary dependencies to keep the project lightweight.

## Testing Standards

### Test Coverage
- **Unit Tests**: Every agent and utility function should have unit tests.
- **Integration Tests**: Test the full workflow from API call to database storage.
- **Mock External Services**: Mock external API calls in tests to avoid rate limits and dependencies.

### Test Quality
- **Test Names**: Use descriptive test names that explain what is being tested.
- **Arrange-Act-Assert**: Follow AAA pattern in test structure.
- **Fixtures**: Use pytest fixtures for common setup/teardown logic.
- **Isolation**: Tests should be independent and runnable in any order.
