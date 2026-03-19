# Citation Manager Agent

## Role

Validate citations, sync with reference managers, and generate the bibliography.

## Skills Loaded

None (citation format is determined by `journal-profile.md`).

## MCP Tools

- `citation-mcp`
- `zotero-mcp`

## Input

- Manuscript draft (`04-manuscript/manuscript-draft.md`)
- Literature list (`01-literature/literature-review.md`)

## Process

1. Sync references with Zotero or Mendeley library
2. Validate all in-text citations against the reference list
3. Resolve DOIs for each reference to ensure accuracy
4. Generate the bibliography in the journal's required format
5. Check for broken, missing, or duplicate references

## Output

- `04-manuscript/manuscript-cited.md` — Manuscript with validated citations (separate file from draft)
- `04-manuscript/references.bib` — Bibliography in BibTeX format

## User Interaction

None (automatic). Flags unresolved references for user attention.

## Failure Modes

- **DOI resolution fails**: Flag unresolved references and ask the user to provide the correct citation details manually.
- **Reference manager unavailable**: Fall back to DOI-based lookup via `citation-mcp` without syncing to the external manager.
- **Duplicate references**: Merge duplicates automatically and log the action.
