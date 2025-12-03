# Agent Rules and Guidelines

## User Rules
- **Git Workflow**: Every time substantial changes are made, they must be pushed to the GitHub repository in the branch `nihal-branch` (or "nihal's branch") with proper comments. If the branch is not present, it must be created.

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

## Vercel MCP Instructions

### Documentation & Platform
- **Search**: Use `search_vercel_documentation` for questions about Next.js, Vercel features, pricing, or security.

### Deployment Access
- **Protected Deployments**: If a Vercel URL returns 403/401, use `get_access_to_vercel_url` to generate a shareable link with an auth cookie.
- **Fetch Fallback**: Use `web_fetch_vercel_url` if the environment doesn't support cookies.

### Project Management
- **Discovery**: Use `list_projects` or `list_teams` to find IDs if unknown. Check `.vercel/project.json` if available.

## Sanity MCP Instructions

### Core Agent Principles
- **Persistence**: Keep going until the user's query is completely resolved.
- **Tool Usage**: Use tools to gather information; do not guess.
- **Planning**: Plan approach before tool calls.
- **Resource Clarification**: Always ask which resource (project ID + dataset) to use if multiple are available.
- **Error Handling**: Try different approaches on error; do not apologize, just act.

### Content Handling
- **Schema-First Approach**: Always check `get_schema` before querying or editing to understand document types.
- **Resource Selection**: Explicitly confirm resource selection with the user.
- **Document Creation Limits**: Max 5 documents at a time. Use `async=true` for multiple creations.

### Searching for Content
- **Schema-First Search**: Use schema to find correct types, then `query_documents`.
- **Multi-Step Queries**: For related entities, query the reference first, then the primary content.
- **Schema Awareness**: Check if fields are arrays or single values before querying.

### Working with GROQ Queries
- **Syntax**: Quote computed field names in projections (e.g., `{"title": name}`).
- **Text Search**: Use `match text::query("term")`.
- **Semantic Search**: Use `semantic_search` with embedding indices.

### Document Operations
- **Action-First**: Perform actions immediately using tools (`create_document`, `update_document`, etc.).
- **Document IDs**: Drafts use `drafts.` prefix; releases use `versions.[releaseId].` prefix.
- **Mutation Notes**:
    - References must be patched after creation.
    - Use `unset` to remove references.
    - References require `_type: 'reference'` and `_ref`.

### Releases and Versioning
- Use release tools (`list_releases`, `create_release`, etc.) to manage content staging.
- Query using the appropriate perspective ("raw", "drafts", "published", or release ID).

### Error Handling
- Check document existence, required fields, and permissions.
- Verify GROQ syntax and field types.

### Response Format
- Concise but thorough.
- Format complex data with markdown.
- Explain actions clearly.
