# Contributing to Scholar Flow

Thank you for your interest in contributing! Scholar Flow is designed to be extensible — adding a new discipline, methodology, or data source should be straightforward.

## Ways to Contribute

### Add a Skill
Skills are markdown files that encode domain knowledge. See `skills/README.md` for the template and `docs/skill-authoring.md` for the full guide.

1. Fork the repo
2. Create your skill in the appropriate `skills/<category>/` directory
3. Follow the skill template format
4. Submit a PR with a description of the methodology/standard your skill covers

### Add an MCP Server
MCP servers connect agents to external APIs. Each server is a standalone Python package under `mcp-servers/`.

1. Fork the repo
2. Create a new directory under `mcp-servers/<your-server>/`
3. Follow the structure of existing servers (pyproject.toml, src/, tests/)
4. Include tests that mock external API calls
5. Submit a PR

### Add a Journal Preset
Journal presets are pre-configured profiles for specific journals, saved as skills under `skills/publication/`.

### Report Bugs or Request Features
Use GitHub Issues with the provided templates.

## Development Setup

```bash
git clone https://github.com/<your-fork>/scholar-flow.git
cd scholar-flow
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Code Style

- Python: formatted with `ruff format`, linted with `ruff check`
- Markdown: consistent heading hierarchy, no trailing whitespace
- Commits: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Run `ruff check .` and `pytest`
4. Submit PR with clear description
5. Wait for review

## Code of Conduct

Be respectful, constructive, and welcoming. We're building tools to help researchers — let's be collaborative about it.
