# Getting Started with Scholar Flow

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed and configured
- Python 3.11 or higher
- Git
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

### Quick Setup

```bash
git clone https://github.com/sencersoylu/scholar-flow.git
cd scholar-flow
uv sync
```

### Install Optional Dependencies

```bash
# Statistics scripts (numpy, pandas, scipy, statsmodels, etc.)
uv sync --extra statistics

# Everything (dev + statistics)
uv sync --extra all
```

### Install MCP Servers

Each MCP server is an independent Python package. Install the ones you need:

```bash
# Core servers (recommended)
cd mcp-servers/pubmed-mcp && pip install -e . && cd ../..
cd mcp-servers/arxiv-mcp && pip install -e . && cd ../..
cd mcp-servers/semantic-scholar-mcp && pip install -e . && cd ../..
cd mcp-servers/statistics-mcp && pip install -e . && cd ../..
cd mcp-servers/citation-mcp && pip install -e . && cd ../..

# Optional servers
cd mcp-servers/journal-parser-mcp && pip install -e . && cd ../..
cd mcp-servers/document-export-mcp && pip install -e . && cd ../..
```

## Configuration

### API Keys

Copy the environment template and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your keys. **All keys are optional** — the system works without them but with reduced functionality:

| Key | Service | What It Enables | How to Get |
|:----|:--------|:----------------|:-----------|
| `NCBI_API_KEY` | PubMed | Faster search (10 req/s vs 3 req/s) | [NCBI API Keys](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/) |
| `S2_API_KEY` | Semantic Scholar | Higher rate limits (10 req/s vs 1 req/s) | [S2 API](https://www.semanticscholar.org/product/api) |
| `CROSSREF_EMAIL` | CrossRef | Polite pool access (faster DOI resolution) | Just your email |
| `ZOTERO_API_KEY` | Zotero | Reference manager sync | [Zotero Keys](https://www.zotero.org/settings/keys) |

### Register MCP Servers with Claude Code

Add the servers to your Claude Code settings. Create or edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "pubmed": {
      "command": "python3",
      "args": ["-m", "pubmed_mcp.server"],
      "env": {
        "NCBI_API_KEY": "your-key-here"
      }
    },
    "arxiv": {
      "command": "python3",
      "args": ["-m", "arxiv_mcp.server"]
    },
    "semantic-scholar": {
      "command": "python3",
      "args": ["-m", "semantic_scholar_mcp.server"],
      "env": {
        "S2_API_KEY": "your-key-here"
      }
    },
    "statistics": {
      "command": "python3",
      "args": ["-m", "statistics_mcp.server"]
    },
    "citation": {
      "command": "python3",
      "args": ["-m", "citation_mcp.server"],
      "env": {
        "CROSSREF_EMAIL": "your-email@example.com"
      }
    },
    "journal-parser": {
      "command": "python3",
      "args": ["-m", "journal_parser_mcp.server"]
    },
    "document-export": {
      "command": "python3",
      "args": ["-m", "document_export_mcp.server"]
    }
  }
}
```

Or add them to the project-level settings in `.claude/settings.json` (already configured in this repo).

## Your First Research Project

### Step 1: Start Claude Code

```bash
cd scholar-flow
claude
```

### Step 2: Set Up Your Researcher Profile

Tell the orchestrator about yourself:

```
> I'm a biomedical researcher studying machine learning applications
  in radiology. I prefer APA citation style and write in formal
  academic English.
```

The orchestrator will create your profile in `skills/profile/researcher-profile/SKILL.md`.

### Step 3: Define Your Research

```
> I want to conduct a systematic review on deep learning for chest
  X-ray diagnosis. My target journal is Radiology.
```

The pipeline will:
1. **Journal Analyzer** parses Radiology's author guidelines
2. **Literature Scout** searches PubMed, arXiv, and Semantic Scholar
3. **Research Designer** proposes PRISMA methodology and research questions
4. The orchestrator pauses for your approval

### Step 4: Approve and Continue

At each decision point, the orchestrator asks for your input:

```
> Yes, proceed with the PRISMA protocol. Focus on studies from 2019-2024.
```

### Step 5: Analysis and Writing

Once you provide data (or the literature review is complete):

```
> Here is my dataset: data/chest_xray_studies.csv
  Run the statistical analysis and generate Table 1.
```

The **Statistician** agent will use the statistics scripts and MCP server to:
- Generate descriptive statistics and Table 1
- Run appropriate statistical tests
- Create publication-quality figures

### Step 6: Manuscript and Export

```
> Write the manuscript draft and format for Radiology submission.
```

The pipeline completes:
- **Academic Writer** drafts the manuscript in IMRaD structure
- **Citation Manager** validates all references
- **Peer Reviewer** checks methodology and reporting compliance
- **Document Export** generates the submission package (.docx + .tex + figures)

## Using Individual Tools

You don't have to run the full pipeline. Use individual scripts directly:

### Statistics Scripts

```bash
# Descriptive statistics
python3 skills/statistics/descriptive-statistics/scripts/summary_stats.py \
  --input data.csv --columns age bmi score

# Generate Table 1
python3 skills/statistics/descriptive-statistics/scripts/table1_generator.py \
  --input data.csv --group-column treatment \
  --continuous age bmi score --categorical sex smoking_status

# Power analysis
python3 skills/statistics/power-analysis/scripts/sample_size_calculator.py \
  --test-type t-test-ind --effect-size 0.5 --alpha 0.05 --power 0.80

# T-test
python3 skills/statistics/inferential-statistics/scripts/t_test.py \
  --input data.csv --column outcome --group-column group

# Linear regression
python3 skills/statistics/regression-analysis/scripts/linear_regression.py \
  --input data.csv --target outcome --predictors age bmi treatment
```

### Citation Tools

```bash
# Convert DOI to BibTeX
python3 skills/publication/citation-tools/scripts/doi_to_bibtex.py \
  --doi 10.1038/s41586-023-06600-9

# Get PubMed metadata
python3 skills/publication/citation-tools/scripts/pubmed_metadata.py \
  --pmid 37198476 --format bibtex

# Validate a .bib file
python3 skills/publication/citation-tools/scripts/citation_validator.py \
  --input references.bib --strict
```

## Project Structure

When you start a research project, Scholar Flow creates this structure:

```
your-project/
├── journal-profile.md          # Extracted journal formatting rules
├── 01-literature/
│   ├── search-strategy.md      # Search terms and databases
│   ├── literature-review.md    # Summarized findings
│   ├── prisma-flow.md          # PRISMA flow diagram
│   └── SUMMARY.md              # Key gaps for next agent
├── 02-design/
│   ├── research-design.md      # Study design document
│   ├── ethics-notes.md         # IRB/ethical considerations
│   └── SUMMARY.md
├── 03-analysis/
│   ├── data-dictionary.md      # Variable descriptions
│   ├── cleaned-data/           # Processed datasets
│   ├── statistical-analysis.md # Analysis report
│   ├── figures/                # Generated plots
│   ├── scripts/                # Reproducible analysis code
│   └── SUMMARY.md
├── 04-manuscript/
│   ├── manuscript-draft.md     # IMRaD manuscript
│   ├── manuscript-cited.md     # With validated citations
│   ├── references.bib          # Bibliography
│   └── SUMMARY.md
├── 05-review/
│   ├── review-report.md        # Internal peer review
│   └── revision-response.md    # Response to reviewers
└── 06-export/
    ├── final-manuscript.docx   # Submission-ready Word
    ├── final-manuscript.tex    # Submission-ready LaTeX
    ├── cover-letter.md         # Cover letter
    └── submission-checklist.md # Submission checklist
```

## Customizing Your Profile

Edit these files to personalize Scholar Flow:

- `skills/profile/researcher-profile/SKILL.md` — Your expertise, field, institution
- `skills/profile/writing-preferences/SKILL.md` — Writing style, tone, language
- `skills/profile/tool-preferences/SKILL.md` — Preferred software (Python/R/SPSS)

## Troubleshooting

### MCP server won't start
```bash
# Check if the server is installed
python3 -m pubmed_mcp.server --help

# If not, install it
cd mcp-servers/pubmed-mcp && pip install -e .
```

### API rate limiting
Most APIs work without keys but with lower rate limits. Add API keys to `.env` for better performance.

### Python version issues
Scholar Flow requires Python 3.11+. Check your version:
```bash
python3 --version
```

### Missing dependencies for statistics scripts
```bash
pip install numpy pandas scipy statsmodels matplotlib scikit-learn lifelines
# Or use uv:
uv sync --extra statistics
```

## Next Steps

- Read [docs/skill-authoring.md](skill-authoring.md) to create custom skills
- Read [docs/architecture.md](architecture.md) for the full architecture guide
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute skills, agents, or MCP servers
