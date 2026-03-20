# Scholar Flow Skills

Skills are the knowledge layer of Scholar Flow. They encode domain expertise — methodology protocols, discipline standards, statistical procedures, and formatting rules — that agents load on demand.

## Skill Structure

Each skill lives in its own folder:

```
skills/<category>/<skill-name>/
├── SKILL.md          # Skill definition (frontmatter + protocol)
├── scripts/          # Runnable Python scripts (e.g., statistical analyses)
└── references/       # Detailed reference documents
```

## Skill Categories

| Category | Directory | Count | Purpose |
|----------|-----------|-------|---------|
| Profile | `profile/` | 3 | Researcher identity, preferences, tool choices |
| Methodology | `methodology/` | 12 | Step-by-step research protocols (PRISMA, CONSORT, etc.) |
| Discipline | `discipline/` | 3 | Field-specific rules (medical, engineering, CS) |
| Statistics | `statistics/` | 9 | Analysis procedures, test selection, runnable scripts |
| Publication | `publication/` | 8 | Journal styles, formatting rules, citation tools |
| Quality | `quality/` | 6 | Review checklists and quality control |

## SKILL.md Template

Every `SKILL.md` uses this structure:

```
---
name: skill-name
category: methodology|discipline|statistics|publication|quality|profile
discipline: medical|engineering|cs|general
description: One-line description of what this skill provides
---

# Skill Name

## When to Use
Describe the conditions under which this skill should be loaded.

## Protocol
Step-by-step instructions the agent should follow.

## Checklist
Numbered checklist items the agent must verify.

## References
Links to source guidelines, papers, or standards.
```

## Skills with Scripts

Some skills include runnable Python scripts in their `scripts/` directory:

- **Statistics skills** — `descriptive-statistics`, `inferential-statistics`, `regression-analysis`, `power-analysis` each include CLI tools for common analyses
- **Citation tools** — `publication/citation-tools` includes DOI→BibTeX converter, PubMed metadata extractor, and citation validator

Run any script with `python scripts/<script>.py --help` for usage.

## Authoring a New Skill

See [docs/skill-authoring.md](../docs/skill-authoring.md) for the full guide.

1. Identify which category your skill belongs to
2. Create a new folder: `skills/<category>/<your-skill-name>/`
3. Add a `SKILL.md` following the template above
4. Optionally add `scripts/` for runnable code and `references/` for detailed docs
5. Include references to authoritative sources
6. Submit a PR
