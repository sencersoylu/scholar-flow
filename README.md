<div align="center">

# Scholar Flow

**AI-powered academic research pipeline — from literature review to submission-ready manuscript.**

Built on [Claude Code](https://claude.ai/code) agents and the [Model Context Protocol](https://modelcontextprotocol.io/).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

[Getting Started](#getting-started) · [Architecture](#architecture) · [Agents](#agents) · [Skills](#skills) · [MCP Servers](#mcp-servers) · [Contributing](#contributing)

</div>

---

## What is Scholar Flow?

Scholar Flow is an open-source system of specialized AI agents that guide you through the entire academic research process. Each agent is an expert in one phase of the workflow — literature review, study design, statistical analysis, manuscript writing, and more.

**You bring the ideas and data. Scholar Flow handles the methodology.**

### Key Features

- **10 Specialized Agents** — Each agent masters one phase of the research pipeline
- **40+ Methodology Skills** — PRISMA, CONSORT, STROBE, IMRaD, and more built-in
- **7 Custom MCP Servers** — PubMed, arXiv, Semantic Scholar, statistics engine, citation manager
- **Multi-discipline** — Medical/health sciences and engineering/computer science
- **Journal-adaptive** — Paste any journal's author guidelines, get formatted output
- **Human-in-the-loop** — You make the decisions, agents do the heavy lifting

### The Pipeline

```
┌─────────┐   ┌───────────┐   ┌──────────┐   ┌──────┐   ┌─────────────┐
│ Journal  │──▶│ Literature │──▶│ Research │──▶│ Data │──▶│ Statistician│
│ Analyzer │   │ Scout      │   │ Designer │   │ Prep │   │             │
└─────────┘   └───────────┘   └──────────┘   └──────┘   └──────┬──────┘
                                                               │
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐       │
│ Document │◀──│   Peer   │◀──│ Citation │◀──│Academic │◀──────┘
│  Export  │   │ Reviewer │   │ Manager  │   │ Writer  │
└──────────┘   └──────────┘   └──────────┘   └─────────┘
```

## Getting Started

### Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed
- Python 3.11+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/sencersoylu/scholar-flow.git
cd scholar-flow

# Install dependencies (using uv — recommended)
uv sync

# Or with pip (install individual MCP servers)
cd mcp-servers/pubmed-mcp && pip install -e .
cd mcp-servers/arxiv-mcp && pip install -e .
# ... repeat for each server you need

# Configure API keys (optional, enhances search capabilities)
cp .env.example .env
# Edit .env with your API keys
```

### Quick Start

```bash
# Start Claude Code in the project directory
cd scholar-flow
claude

# Start a new research project
> I want to start a new research project on [your topic]

# The orchestrator will guide you through:
# 1. Setting up your researcher profile
# 2. Selecting target journal
# 3. Running the full pipeline
```

## Architecture

Scholar Flow has three layers:

| Layer | Purpose | Location |
|-------|---------|----------|
| **Agents** | Orchestrate the research workflow | `agents/` |
| **Skills** | Provide domain knowledge and methodology | `skills/` |
| **MCP Servers** | Connect to external APIs and tools | `mcp-servers/` |

```
┌─────────────────────────────────────────────┐
│               Orchestrator                   │
│         (dispatches & coordinates)           │
├─────────────────────────────────────────────┤
│  Agent Layer     │  Skill Layer             │
│  ┌────────────┐  │  ┌────────────────────┐  │
│  │ Lit Scout  │──┼──│ systematic-review  │  │
│  │ Researcher │──┼──│ cohort-study       │  │
│  │ Statistic. │──┼──│ regression-analysis│  │
│  │ Writer     │──┼──│ ama-style          │  │
│  │ ...        │  │  │ ...                │  │
│  └────────────┘  │  └────────────────────┘  │
├─────────────────────────────────────────────┤
│  MCP Server Layer                            │
│  ┌──────────┬──────────┬──────────────────┐  │
│  │ PubMed   │ arXiv    │ Semantic Scholar │  │
│  │ Stats    │ Citation │ Journal Parser   │  │
│  └──────────┴──────────┴──────────────────┘  │
└─────────────────────────────────────────────┘
```

See [docs/architecture.md](docs/architecture.md) for the full architecture guide.

## Agents

| Agent | Role |
|-------|------|
| **Orchestrator** | Coordinates the pipeline, manages user interaction |
| **Journal Analyzer** | Parses journal templates and author guidelines |
| **Literature Scout** | Searches PubMed, arXiv, Semantic Scholar, Scopus, IEEE Xplore |
| **Research Designer** | Formulates research questions, hypotheses, study design |
| **Data Preparator** | Cleans, validates, and prepares datasets for analysis |
| **Statistician** | Runs statistical analyses with Python/R, generates figures |
| **Academic Writer** | Writes manuscripts in IMRaD structure per journal format |
| **Citation Manager** | Manages references via Zotero, validates citations |
| **Peer Reviewer** | Reviews methodology, statistics, and reporting compliance |
| **Document Export** | Converts to Word/LaTeX, prepares submission package |
| **Revision Agent** | Handles journal revision responses point-by-point |

## Skills

Skills are the knowledge layer — methodology protocols, discipline standards, and formatting rules that agents load on demand.

| Category | Count | Examples |
|----------|-------|---------|
| **Profile** | 3 | researcher-profile, writing-preferences, tool-preferences |
| **Methodology** | 12 | systematic-review, meta-analysis, RCT, cohort-study, case-report |
| **Discipline** | 3 | medical-standards, engineering-standards, cs-standards |
| **Statistics** | 9 | inferential-statistics, regression, survival-analysis, bayesian |
| **Publication** | 7 | ama-style, ieee-style, acm-style, journal-selector |
| **Quality** | 6 | peer-review, statistical-review, reporting-checklist |

**Adding your own skill?** See [docs/skill-authoring.md](docs/skill-authoring.md).

## MCP Servers

| Server | API | Purpose |
|--------|-----|---------|
| `pubmed-mcp` | NCBI E-utilities | Medical literature search, MeSH terms |
| `arxiv-mcp` | arXiv API | Preprint search, PDF/LaTeX retrieval |
| `semantic-scholar-mcp` | Semantic Scholar | Citation graphs, related papers |
| `statistics-mcp` | Python/R runtime | Statistical analysis execution |
| `journal-parser-mcp` | python-docx, LaTeX parser | Template parsing |
| `citation-mcp` | CrossRef, BibTeX | Reference management |
| `document-export-mcp` | Pandoc, python-docx | Final document generation |

## Supported Disciplines

### Medical / Health Sciences
RCT, cohort studies, case-control, systematic reviews, meta-analyses, case reports. CONSORT, STROBE, PRISMA, CARE checklists. MeSH terminology, ICMJE standards.

### Engineering / Computer Science
Experimental studies, computational studies, algorithm benchmarks, ablation studies. IEEE/ACM standards, artifact evaluation, reproducibility requirements.

## Contributing

We welcome contributions! Whether it's a new skill for your discipline, an MCP server for a new data source, or improvements to existing agents.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ideas for Contributions
- Skills for new disciplines (social sciences, economics, law)
- MCP servers for new databases (Web of Science, DBLP, Cochrane)
- Journal style presets for popular journals
- Translations of methodology skills

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with [Claude Code](https://claude.ai/code) and [MCP](https://modelcontextprotocol.io/)**

</div>
