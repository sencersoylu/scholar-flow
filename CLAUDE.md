# Scholar Flow — Claude Code Project Instructions

## Project Overview
Scholar Flow is an AI-powered academic research pipeline built on Claude Code agents and MCP servers. It automates the full research workflow from literature review to submission-ready manuscripts.

## Architecture
- `agents/` — Claude Code agent definitions (markdown). Each file defines one specialized agent.
- `skills/` — Knowledge layer (markdown). Skills provide domain expertise that agents consume.
- `mcp-servers/` — Python-based MCP servers. Each subdirectory is an independent Python package.
- `templates/` — Scaffolding for new academic projects.
- `docs/` — Architecture docs, guides, tutorials.

## Development Commands
- **Run MCP server tests:** `cd mcp-servers/<server-name> && pytest`
- **Lint:** `ruff check .`
- **Format:** `ruff format .`

## Conventions
- Agent definitions follow the template in `agents/README.md`
- Skills follow the template in `skills/README.md`
- MCP servers use the MCP Python SDK with stdio transport
- All MCP servers have `src/<package_name>/server.py` as entry point
- Tests go in `tests/` within each MCP server directory
- Commit style: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- Academic project commits: `[academic/<project>] <agent-name>: <brief description>`
