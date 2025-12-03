# <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=dL3M6FPblFer&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=dL3M6FPblFer&format=png&size=48" height="32"/></picture> Agent Rules & Guidelines

Welcome to the **TribeCode-Test** project! This repository follows specific guidelines to ensure efficient development, seamless integration with MCP tools (Sanity, Vercel), and a clean git workflow.

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=2906&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=2906&format=png&size=48" height="24"/></picture> User Rules

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=38388&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=38388&format=png&size=48" height="20"/></picture> Git Workflow
- **Branching Strategy**: All substantial changes must be pushed to the branch `nihal-branch`.
- **Commit Policy**: If the branch doesn't exist, it is created automatically. Changes are committed with descriptive messages and pushed immediately.

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=11151&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=11151&format=png&size=48" height="24"/></picture> General Agent Guidelines

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=11151&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=11151&format=png&size=48" height="20"/></picture> Tool Usage
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48" height="16"/></picture> Natural Language**: We describe actions naturally without referencing internal tool names.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=6697&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=6697&format=png&size=48" height="16"/></picture> Specialized Tools**: We prefer specific file operations (`read_file`) over generic shell commands.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48" height="16"/></picture> Parallelism**: Independent operations are executed in parallel to save time.

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="20"/></picture> Code Editing & Exploration
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/></picture> Semantic Search**: We start broad and narrow down, ensuring we find the right context.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48" height="16"/></picture> Context Awareness**: We trace symbols and understand the "full picture" before making edits.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=6697&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=6697&format=png&size=48" height="16"/></picture> Style & Conventions**: We respect existing coding patterns and fix any linter errors we introduce.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48" height="16"/></picture> No Reverts**: We trust the user's direction and do not revert changes unless asked.

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=38536&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=38536&format=png&size=48" height="24"/></picture> Browser & Testing Guidelines

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=38536&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=38536&format=png&size=48" height="20"/></picture> Testing Flow
1.  **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=38536&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=38536&format=png&size=48" height="16"/></picture> Navigate**: Go to the target page.
2.  **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48" height="16"/></picture> Snapshot**: Capture the page state.
3.  **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48" height="16"/></picture> Interact**: Click, type, or trigger events.
4.  **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48" height="16"/></picture> Re-snapshot**: Verify the outcome.
5.  **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48" height="16"/></picture> Visual Inspection**: Take screenshots when visual verification is needed.

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48" height="20"/></picture> Restrictions
- No local server startup unless requested.
- No port guessing.
- No shell interaction for browser tasks.

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=11788&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=11788&format=png&size=48" height="24"/></picture> Vercel MCP Instructions

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48" height="20"/></picture> Documentation & Platform
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/></picture> Search**: We use documentation tools for Next.js and Vercel-specific queries.

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=GENqO55M9bA9&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=GENqO55M9bA9&format=png&size=48" height="20"/></picture> Deployment Access
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48" height="16"/></picture> Protected Deployments**: We handle 403/401 errors by generating shareable links with auth cookies.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48" height="16"/></picture> Fetch Fallback**: We have fallback mechanisms for environments without cookie support.

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=11151&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=11151&format=png&size=48" height="20"/></picture> Project Management
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/></picture> Discovery**: We actively discover project and team IDs to ensure smooth operations.

---

## <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48" height="24"/></picture> Sanity MCP Instructions

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=dL3M6FPblFer&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=dL3M6FPblFer&format=png&size=48" height="20"/></picture> Core Agent Principles
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=38388&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=38388&format=png&size=48" height="16"/></picture> Persistence**: We don't stop until the query is resolved.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/></picture> No Guessing**: We use tools to get facts.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48" height="16"/></picture> Planning**: We plan before we act.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/></picture> Resource Clarification**: We always ask which project/dataset to use.

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=1671&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=1671&format=png&size=48" height="20"/></picture> Content Handling
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=DHOunydDcKfC&format=png&size=48" height="16"/></picture> Schema-First**: We check the schema (`get_schema`) before touching content.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=2906&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=2906&format=png&size=48" height="16"/></picture> Explicit Confirmation**: We confirm resources with you.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48" height="16"/></picture> Limits**: We batch document creation (max 5) and use async modes.

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="20"/></picture> Searching for Content
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=WwWusvLMTFd7&format=png&size=48" height="16"/></picture> Precision**: We find the right types first.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=kktvCbkDLbNb&format=png&size=48" height="16"/></picture> Multi-Step**: We resolve references before querying primary content.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48" height="16"/></picture> Structure Awareness**: We check for arrays vs. single values.

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=6697&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=6697&format=png&size=48" height="20"/></picture> Document Operations & GROQ
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48" height="16"/></picture> Action-First**: We perform creates/updates immediately.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=gxuEDgFteZdP&format=png&size=48" height="16"/></picture> ID Handling**: We respect draft and release ID prefixes.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=6697&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=6697&format=png&size=48" height="16"/></picture> Mutation Safety**: We handle references carefully (patch after create, use `unset`).
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=mcCRHk2xvR7f&format=png&size=48" height="16"/></picture> GROQ Syntax**: We use proper quoting and search syntax (`match text`).

### <picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=GENqO55M9bA9&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=GENqO55M9bA9&format=png&size=48" height="20"/></picture> Releases & Versioning
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=91AOdnippsUN&format=png&size=48" height="16"/></picture> Staging**: We use releases to manage content updates.
- **<picture><source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48&color=ffffff"><img src="https://img.icons8.com/?id=vmqv135kp5Ty&format=png&size=48" height="16"/></picture> Perspectives**: We query the right view (drafts, published, release).

---

*This README is auto-generated based on the `agent.md` rules file.*
