<div align="center">

# Scholar Flow

**AI-powered academic research pipeline — from literature review to submission-ready manuscript.**

Built on [Claude Code](https://claude.ai/code) agents and the [Model Context Protocol](https://modelcontextprotocol.io/).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![Skills: 44+](https://img.shields.io/badge/Skills-44%2B-purple.svg)](#skills)

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

**Quick setup (one command):**

```bash
git clone https://github.com/sencersoylu/scholar-flow.git && cd scholar-flow && uv sync
```

<details>
<summary><strong>Detailed installation</strong></summary>

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

</details>

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

## Real Usage Examples

### Example 1: Systematic Review on Machine Learning in Radiology

```
You:    I want to conduct a systematic review on machine learning applications
        in chest X-ray diagnosis. Target journal: Radiology.

Agent:  ── Journal Analyzer ──
        Parsed Radiology author guidelines: structured abstract (≤300 words),
        STARD/PRISMA checklist required, AMA citation style.

        ── Literature Scout ──
        Searching PubMed (MeSH: "Machine Learning" AND "Radiography, Thoracic")…
        Searching arXiv (cs.CV + medical imaging)…
        Found 847 candidate papers → 312 after deduplication → 42 after
        title/abstract screening against your PICO criteria.

        ── Research Designer ──
        Proposed PRISMA 2020 flow diagram. Registered protocol fields drafted.
        Ready for your review before full-text screening begins.
```

### Example 2: Power Analysis for a Clinical Trial

```
You:    Run a power analysis for a two-arm RCT comparing a new antibiotic vs
        standard of care. Primary outcome: infection clearance at 14 days.
        Expected effect size: 15% absolute difference (70% vs 85%).

Agent:  ── Statistician (stats skill) ──
        Invoked statistics-mcp → power_analysis tool
        ┌──────────────────────────────────────┐
        │ Two-proportion z-test (two-sided)    │
        │ Alpha: 0.05 | Power: 0.80           │
        │ p1 = 0.70, p2 = 0.85               │
        │ Required n per arm: 133             │
        │ Total (with 10% dropout): 296       │
        └──────────────────────────────────────┘
        Generated script: outputs/power_analysis.py
        Recommend: also run sensitivity analysis across effect sizes 10–20%.
```

### Example 3: Format Manuscript for IEEE Access

```
You:    My manuscript draft is in outputs/draft.md. Format it for IEEE Access
        and prepare the submission package.

Agent:  ── Academic Writer ──
        Loaded ieee-style skill. Restructured to IMRaD with IEEE headings.
        Abstract condensed to 200 words. Keywords: 5 IEEE-index terms added.

        ── Citation Manager ──
        Converted 38 references to IEEE numbered style via citation-mcp.
        Verified DOIs for all entries — 2 corrections applied.

        ── Document Export ──
        Generated via document-export-mcp:
          • outputs/manuscript_ieee.docx  (IEEE Access template)
          • outputs/manuscript_ieee.tex   (LaTeX two-column)
          • outputs/figures/              (300 dpi TIF, per journal spec)
          • outputs/cover_letter.docx
        Submission checklist: 12/12 items passed.
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
| **Discipline** | 6 | medical, engineering, CS, social sciences, economics, law |
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

## How Scholar Flow Compares

| Feature | Scholar Flow | claude-scientific-skills | Manual Workflow |
|---------|-------------|------------------------|-----------------|
| Full pipeline orchestration | Yes | No (skills only) | No |
| MCP server integration | 7 servers | No | N/A |
| Runnable analysis scripts | Yes | Yes | Write your own |
| Multi-discipline | Medical + Engineering + CS | Science-focused | Varies |
| Journal-adaptive formatting | Yes | Partial | Manual |

## Contributing

We welcome contributions! Whether it's a new skill for your discipline, an MCP server for a new data source, or improvements to existing agents.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ideas for Contributions
- Skills for new disciplines (social sciences, economics, law)
- MCP servers for new databases (Web of Science, DBLP, Cochrane)
- Journal style presets for popular journals
- Translations of methodology skills

## Citation

If Scholar Flow assists your research, please cite:

```bibtex
@software{scholar_flow,
  title = {Scholar Flow: AI-Powered Academic Research Pipeline},
  author = {Soylu, Sencer},
  year = {2025},
  url = {https://github.com/sencersoylu/scholar-flow},
  note = {Built on Claude Code agents and the Model Context Protocol}
}
```

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with [Claude Code](https://claude.ai/code) and [MCP](https://modelcontextprotocol.io/)**

</div>
