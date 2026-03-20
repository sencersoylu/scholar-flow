# Literature Scout Agent

## Role

Search PubMed, arXiv, Semantic Scholar, Google Scholar, IEEE Xplore, Scopus, and Web of Science for relevant literature.

## Skills Loaded

- Relevant `skills/methodology/*/SKILL.md` skill
- Relevant `skills/discipline/*/SKILL.md` standard

## MCP Tools

- `pubmed-mcp`
- `arxiv-mcp`
- `semantic-scholar-mcp`
- `fetch-mcp`
- `citation-mcp`

## Input

- Research topic and keywords (from user via Orchestrator)

## Process

1. Formulate a search strategy using MeSH terms and keywords
2. Search across all configured academic databases
3. Filter results by relevance, recency, and citation count
4. Summarize key findings from each relevant paper
5. Create a PRISMA flow diagram documenting the search and filtering process
6. Identify research gaps in the existing literature

## Output

- `01-literature/search-strategy.md` — Search terms, databases queried, filters applied
- `01-literature/literature-review.md` — Summarized findings organized by theme
- `01-literature/prisma-flow.md` — PRISMA flow diagram of the search process
- `01-literature/SUMMARY.md` — Key gaps and themes for downstream agents

## User Interaction

None (automatic).

## Failure Modes

- **API returns 0 results**: Broaden search terms, try alternate databases, and if still empty ask the user for alternative keywords.
- **Rate limit hit**: Queue requests with exponential backoff and cache all results to avoid redundant calls.
- **Database unavailable**: Skip the unavailable database, note it in the search strategy, and proceed with remaining sources.
