# Authoring Custom Skills

## What is a Skill?

A skill is a markdown file that encodes domain expertise — methodology protocols, discipline standards, statistical procedures, or formatting rules. Agents load relevant skills to guide their work.

## Skill Template

Every skill uses this frontmatter format:

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
| Statistics | `skills/statistics/` | Analysis procedures and test selection guides |
| Publication | `skills/publication/` | Citation styles and journal formatting |
| Quality | `skills/quality/` | Review checklists and quality assurance |

## Best Practices

- Reference authoritative sources (guidelines, textbooks, standards)
- Include a "When to Use" section so agents know when to load the skill
- Provide step-by-step protocols, not just descriptions
- Include checklists where applicable
- Keep skills focused — one methodology per file

## Examples

> TODO: Add annotated examples after first skills are fully implemented

## Testing Your Skill

> TODO: Document skill testing approach
