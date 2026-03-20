# Authoring Custom Skills

## What is a Skill?

A skill is a folder that encodes domain expertise — methodology protocols, discipline standards, statistical procedures, or formatting rules. Agents load relevant skills to guide their work. Each skill folder contains a `SKILL.md` definition and optionally includes runnable scripts and reference documents.

## Skill Folder Structure

```
skills/<category>/<skill-name>/
├── SKILL.md          # Required — skill definition with frontmatter
├── scripts/          # Optional — runnable Python scripts
└── references/       # Optional — detailed reference documents
```

## SKILL.md Frontmatter

Every `SKILL.md` uses this frontmatter format:

```yaml
---
name: skill-name
category: methodology|discipline|statistics|publication|quality|profile
discipline: medical|engineering|cs|general
description: One-line description
---
```

## Categories

| Category | Directory | What Goes Here |
|----------|-----------|---------------|
| Profile | `skills/profile/` | Researcher preferences and tool choices |
| Methodology | `skills/methodology/` | Research design protocols (PRISMA, CONSORT, etc.) |
| Discipline | `skills/discipline/` | Field-specific rules and standards |
| Statistics | `skills/statistics/` | Analysis procedures, test selection, runnable scripts |
| Publication | `skills/publication/` | Citation styles, journal formatting, citation tools |
| Quality | `skills/quality/` | Review checklists and quality assurance |

## Best Practices

- Reference authoritative sources (guidelines, textbooks, standards)
- Include a "When to Use" section so agents know when to load the skill
- Provide step-by-step protocols, not just descriptions
- Include checklists where applicable
- Keep skills focused — one methodology per file

## Annotated Example: `systematic-review`

The `skills/methodology/systematic-review/SKILL.md` skill is a fully implemented example. Below is a walkthrough of how it is structured and why.

### Frontmatter

```yaml
---
name: systematic-review
category: methodology
discipline: general
description: "PRISMA 2020 systematic review protocol with database search strategy and bias assessment"
---
```

| Field | Purpose |
|-------|---------|
| `name` | Unique identifier used by agents to load the skill. Use lowercase kebab-case. |
| `category` | One of the six categories listed above. Determines the directory the file lives in (`skills/<category>/`). |
| `discipline` | Scope limiter. Use `general` when the skill applies across fields, or a specific discipline (e.g., `medical`, `cs`) to restrict agent selection. |
| `description` | A single sentence agents use to decide whether this skill is relevant to the current task. Be precise — vague descriptions lead to incorrect skill loading. |

### Body Structure

A well-formed skill body follows this three-part pattern:

#### 1. When to Use

A short paragraph describing the scenario that should trigger skill loading. Agents match the user's task description against this section.

```markdown
## When to Use
When conducting a systematic review of existing literature to answer a clearly
defined research question. Applicable across disciplines...
```

**Why it matters:** Without this section, agents must rely solely on the `description` field, which may not capture edge cases.

#### 2. Protocol (numbered steps)

The core content. Each step should be:
- **Actionable** — tells the agent what to *do*, not just what to *know*
- **Sequenced** — steps follow the natural workflow order
- **Detailed** — includes sub-bullets for specific actions, tool names, thresholds, and decision criteria

```markdown
## Protocol

### Step 1: Define the Research Question
- Formulate a focused question using the PICO(S) framework:
  - **P**opulation: Who is being studied?
  - **I**ntervention / Exposure: What is the treatment, exposure, or phenomenon?
  ...
```

**Tip:** Cross-reference other skills where workflows overlap. For example, `systematic-review.md` says "proceed to meta-analysis (see meta-analysis skill)" rather than duplicating that protocol.

#### 3. Checklist

A numbered checklist that agents (and human reviewers) can verify against. In the systematic-review skill this is the full PRISMA 2020 27-item checklist, organized by manuscript section (Title, Abstract, Introduction, Methods, Results, Discussion, Other Information).

```markdown
## Checklist: PRISMA 2020 (27 Items)

### Title
1. Identify the report as a systematic review

### Abstract
2. Provide a structured abstract...
```

**Why it matters:** Checklists give agents a concrete completion test. An agent can iterate through each item and confirm the manuscript satisfies it.

#### 4. References

Cite the authoritative sources the skill is based on. Use full citations so agents can include them in generated manuscripts.

```markdown
## References
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement...
- Higgins JPT, Thomas J, Chandler J, et al. Cochrane Handbook...
```

### Summary of the Pattern

```
---
frontmatter (name, category, discipline, description)
---

# Skill Title

## When to Use        ← trigger conditions for agents
## Protocol           ← step-by-step instructions (the core)
## Checklist          ← verification items (optional but recommended)
## References         ← authoritative sources
```

## Adding Scripts to a Skill

Some skills benefit from runnable Python scripts — especially statistics and citation tools. Place scripts in the `scripts/` subdirectory:

```
skills/statistics/descriptive-statistics/
├── SKILL.md
├── scripts/
│   ├── summary_stats.py
│   ├── normality_test.py
│   └── table1_generator.py
└── references/
```

Script conventions:
- Add `#!/usr/bin/env python3` shebang
- Use `argparse` for CLI arguments
- Include a docstring with usage examples
- Prefer stdlib-only dependencies where possible; use `numpy`, `scipy`, `statsmodels`, `pandas` for statistics
- Include `if __name__ == "__main__":` block

## Testing Your Skill

1. **Frontmatter validation** — Verify all four required fields (`name`, `category`, `discipline`, `description`) are present and the `category` matches the directory the skill folder is in.

2. **Dry-run with an agent** — Use the research-design agent or methodology-advisor agent and describe a task that should trigger your skill. Confirm the agent loads the correct skill and follows the protocol steps.

3. **Script testing** — If your skill includes scripts, verify they run with `python scripts/<name>.py --help` and produce expected output.

4. **Checklist pass** — If your skill includes a checklist, generate a sample output and verify every checklist item is addressed.

5. **Cross-reference check** — If your skill references other skills (e.g., "see meta-analysis skill"), verify those skills exist and the names match.

6. **Peer review** — Have a domain expert review the protocol for accuracy against current guidelines. Skills encode expert knowledge, so factual correctness is critical.
