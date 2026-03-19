# Scholar Flow Skills

Skills are the knowledge layer of Scholar Flow. They encode domain expertise — methodology protocols, discipline standards, statistical procedures, and formatting rules — that agents load on demand.

## Skill Categories

| Category | Directory | Purpose |
|----------|-----------|---------|
| Profile | `profile/` | Researcher identity, preferences, tool choices |
| Methodology | `methodology/` | Step-by-step research protocols (PRISMA, CONSORT, etc.) |
| Discipline | `discipline/` | Field-specific rules (medical, engineering, CS) |
| Statistics | `statistics/` | Analysis procedures and test selection |
| Publication | `publication/` | Journal styles and formatting rules |
| Quality | `quality/` | Review checklists and quality control |

## Skill Template

Every skill file uses this structure:

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

## Authoring a New Skill

See [docs/skill-authoring.md](../docs/skill-authoring.md) for the full guide.

1. Identify which category your skill belongs to
2. Create a new `.md` file in the appropriate directory
3. Follow the skill template above
4. Include references to authoritative sources
5. Submit a PR
