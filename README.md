# <img src="https://img.icons8.com/?id=dL3M6FPblFer&format=png&size=48" height="32"/> Agent Rules & Guidelines

Welcome to the **TribeCode-Test** project! This repository follows specific guidelines to ensure efficient development, seamless integration with MCP tools (Sanity, Vercel), and a clean git workflow.

---

## <img src="https://img.icons8.com/?id=2906&format=png&size=48" height="24"/> User Rules

### <img src="https://img.icons8.com/?id=38388&format=png&size=48" height="20"/> Git Workflow
- **Branching Strategy**: All substantial changes must be pushed to the branch `nihal-branch`.
- **Commit Policy**: If the branch doesn't exist, it is created automatically. Changes are committed with descriptive messages and pushed immediately.

---

## <img src="https://img.icons8.com/?id=11151&format=png&size=48" height="24"/> General Agent Guidelines

### <img src="https://img.icons8.com/?id=11151&format=png&size=48" height="20"/> Tool Usage
- **<img src="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48" height="16"/> Natural Language**: We describe actions naturally without referencing internal tool names.
- **<img src="https://img.icons8.com/?id=6697&format=png&size=48" height="16"/> Specialized Tools**: We prefer specific file operations (`read_file`) over generic shell commands.
- **<img src="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48" height="16"/> Parallelism**: Independent operations are executed in parallel to save time.

### <img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="20"/> Code Editing & Exploration
- **<img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/> Semantic Search**: We start broad and narrow down, ensuring we find the right context.
- **<img src="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48" height="16"/> Context Awareness**: We trace symbols and understand the "full picture" before making edits.
- **<img src="https://img.icons8.com/?id=6697&format=png&size=48" height="16"/> Style & Conventions**: We respect existing coding patterns and fix any linter errors we introduce.
- **<img src="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48" height="16"/> No Reverts**: We trust the user's direction and do not revert changes unless asked.

---

## <img src="https://img.icons8.com/?id=38536&format=png&size=48" height="24"/> Browser & Testing Guidelines

### <img src="https://img.icons8.com/?id=38536&format=png&size=48" height="20"/> Testing Flow
1.  **<img src="https://img.icons8.com/?id=38536&format=png&size=48" height="16"/> Navigate**: Go to the target page.
2.  **<img src="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48" height="16"/> Snapshot**: Capture the page state.
3.  **<img src="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48" height="16"/> Interact**: Click, type, or trigger events.
4.  **<img src="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48" height="16"/> Re-snapshot**: Verify the outcome.
5.  **<img src="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48" height="16"/> Visual Inspection**: Take screenshots when visual verification is needed.

### <img src="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48" height="20"/> Restrictions
- No local server startup unless requested.
- No port guessing.
- No shell interaction for browser tasks.

---

## <img src="https://img.icons8.com/?id=11788&format=png&size=48" height="24"/> Vercel MCP Instructions

### <img src="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48" height="20"/> Documentation & Platform
- **<img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/> Search**: We use documentation tools for Next.js and Vercel-specific queries.

### <img src="https://img.icons8.com/?id=GENqO55M9bA9&format=png&size=48" height="20"/> Deployment Access
- **<img src="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48" height="16"/> Protected Deployments**: We handle 403/401 errors by generating shareable links with auth cookies.
- **<img src="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48" height="16"/> Fetch Fallback**: We have fallback mechanisms for environments without cookie support.

### <img src="https://img.icons8.com/?id=11151&format=png&size=48" height="20"/> Project Management
- **<img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/> Discovery**: We actively discover project and team IDs to ensure smooth operations.

---

## <img src="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48" height="24"/> Sanity MCP Instructions

### <img src="https://img.icons8.com/?id=dL3M6FPblFer&format=png&size=48" height="20"/> Core Agent Principles
- **<img src="https://img.icons8.com/?id=38388&format=png&size=48" height="16"/> Persistence**: We don't stop until the query is resolved.
- **<img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/> No Guessing**: We use tools to get facts.
- **<img src="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48" height="16"/> Planning**: We plan before we act.
- **<img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/> Resource Clarification**: We always ask which project/dataset to use.

### <img src="https://img.icons8.com/?id=1671&format=png&size=48" height="20"/> Content Handling
- **<img src="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48" height="16"/> Schema-First**: We check the schema (`get_schema`) before touching content.
- **<img src="https://img.icons8.com/?id=2906&format=png&size=48" height="16"/> Explicit Confirmation**: We confirm resources with you.
- **<img src="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48" height="16"/> Limits**: We batch document creation (max 5) and use async modes.

### <img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="20"/> Searching for Content
- **<img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/> Precision**: We find the right types first.
- **<img src="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48" height="16"/> Multi-Step**: We resolve references before querying primary content.
- **<img src="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48" height="16"/> Structure Awareness**: We check for arrays vs. single values.

### <img src="https://img.icons8.com/?id=6697&format=png&size=48" height="20"/> Document Operations & GROQ
- **<img src="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48" height="16"/> Action-First**: We perform creates/updates immediately.
- **<img src="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48" height="16"/> ID Handling**: We respect draft and release ID prefixes.
- **<img src="https://img.icons8.com/?id=6697&format=png&size=48" height="16"/> Mutation Safety**: We handle references carefully (patch after create, use `unset`).
- **<img src="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48" height="16"/> GROQ Syntax**: We use proper quoting and search syntax (`match text`).

### <img src="https://img.icons8.com/?id=GENqO55M9bA9&format=png&size=48" height="20"/> Releases & Versioning
- **<img src="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48" height="16"/> Staging**: We use releases to manage content updates.
- **<img src="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48" height="16"/> Perspectives**: We query the right view (drafts, published, release).

---

*This README is auto-generated based on the `agent.md` rules file.*
