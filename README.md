# 🤖 Agent Rules & Guidelines

Welcome to the **TribeCode-Test** project! This repository follows specific guidelines to ensure efficient development, seamless integration with MCP tools (Sanity, Vercel), and a clean git workflow.

---

## 👤 User Rules

### 🐙 Git Workflow
- **Branching Strategy**: All substantial changes must be pushed to the branch `nihal-branch`.
- **Commit Policy**: If the branch doesn't exist, it is created automatically. Changes are committed with descriptive messages and pushed immediately.

---

## 🧭 General Agent Guidelines

### 🛠️ Tool Usage
- **🗣️ Natural Language**: We describe actions naturally without referencing internal tool names.
- **🧰 Specialized Tools**: We prefer specific file operations (`read_file`) over generic shell commands.
- **⚡ Parallelism**: Independent operations are executed in parallel to save time.

### 🔍 Code Editing & Exploration
- **🔎 Semantic Search**: We start broad and narrow down, ensuring we find the right context.
- **🧩 Context Awareness**: We trace symbols and understand the "full picture" before making edits.
- **🎨 Style & Conventions**: We respect existing coding patterns and fix any linter errors we introduce.
- **🔙 No Reverts**: We trust the user's direction and do not revert changes unless asked.

---

## 🌐 Browser & Testing Guidelines

### 🧪 Testing Flow
1.  **🧭 Navigate**: Go to the target page.
2.  **📸 Snapshot**: Capture the page state.
3.  **🖱️ Interact**: Click, type, or trigger events.
4.  **🔄 Re-snapshot**: Verify the outcome.
5.  **👀 Visual Inspection**: Take screenshots when visual verification is needed.

### 🚫 Restrictions
- No local server startup unless requested.
- No port guessing.
- No shell interaction for browser tasks.

---

## ▲ Vercel MCP Instructions

### 📚 Documentation & Platform
- **🔍 Search**: We use documentation tools for Next.js and Vercel-specific queries.

### 🚀 Deployment Access
- **🔐 Protected Deployments**: We handle 403/401 errors by generating shareable links with auth cookies.
- **📡 Fetch Fallback**: We have fallback mechanisms for environments without cookie support.

### 📂 Project Management
- **🆔 Discovery**: We actively discover project and team IDs to ensure smooth operations.

---

## 📝 Sanity MCP Instructions

### 🧠 Core Agent Principles
- **💪 Persistence**: We don't stop until the query is resolved.
- **🤔 No Guessing**: We use tools to get facts.
- **📋 Planning**: We plan before we act.
- **❓ Resource Clarification**: We always ask which project/dataset to use.

### 📦 Content Handling
- **📑 Schema-First**: We check the schema (`get_schema`) before touching content.
- **✋ Explicit Confirmation**: We confirm resources with you.
- **🚦 Limits**: We batch document creation (max 5) and use async modes.

### 🔎 Searching for Content
- **🎯 Precision**: We find the right types first.
- **🔗 Multi-Step**: We resolve references before querying primary content.
- **🔢 Structure Awareness**: We check for arrays vs. single values.

### 💾 Document Operations & GROQ
- **⚡ Action-First**: We perform creates/updates immediately.
- **🆔 ID Handling**: We respect draft and release ID prefixes.
- **📝 Mutation Safety**: We handle references carefully (patch after create, use `unset`).
- **🏷️ GROQ Syntax**: We use proper quoting and search syntax (`match text`).

### 🚀 Releases & Versioning
- **📦 Staging**: We use releases to manage content updates.
- **👀 Perspectives**: We query the right view (drafts, published, release).

---

*This README is auto-generated based on the `agent.md` rules file.*

