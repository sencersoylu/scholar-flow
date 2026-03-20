"""Reference management via CrossRef/BibTeX MCP Server."""

import json
import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from citation_mcp.bibtex import format_bibtex, parse_bibtex, validate_bibtex
from citation_mcp.cache import ResponseCache
from citation_mcp.client import CrossRefClient
from citation_mcp.models import Reference

mcp = FastMCP("citation-mcp")

_client = CrossRefClient()
_cache_dir = Path(os.environ.get("SCHOLAR_FLOW_CACHE_DIR", "/tmp/scholar-flow-cache/citation"))
_cache = ResponseCache(cache_dir=_cache_dir, ttl_seconds=86400)


@mcp.tool()
async def resolve_doi(doi: str) -> str:
    """Resolve DOI to full citation metadata via CrossRef.

    Returns formatted markdown with the full citation details and a BibTeX entry.
    """
    cache_key = f"doi:{doi}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    try:
        ref = await _client.resolve_doi(doi)
    except Exception as e:
        return f"**Error resolving DOI `{doi}`:** {e}"

    bibtex = format_bibtex(ref)
    md = (
        f"## DOI Resolution: {doi}\n\n"
        f"{ref.to_markdown()}\n"
        f"### BibTeX\n\n```bibtex\n{bibtex}\n```\n"
    )
    _cache.set(cache_key, {"result": md})
    return md


@mcp.tool()
async def parse_bibtex_file(file_path: str) -> str:
    """Parse a BibTeX file and return structured references.

    Returns a markdown summary of all entries found, plus any validation issues.
    """
    path = Path(file_path)
    if not path.exists():
        return f"**Error:** File not found: `{file_path}`"

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"**Error reading file:** {e}"

    refs = parse_bibtex(text)
    if not refs:
        return f"**No BibTeX entries found in** `{file_path}`."

    issues = validate_bibtex(text)

    parts = [f"## BibTeX File: `{path.name}`\n", f"Found **{len(refs)}** entries.\n"]

    for ref in refs:
        parts.append(ref.to_markdown())
        parts.append("---\n")

    if issues:
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        parts.append(f"## Validation: {len(errors)} error(s), {len(warnings)} warning(s)\n")
        for issue in issues:
            parts.append(issue.to_markdown())
    else:
        parts.append("## Validation: No issues found")

    return "\n".join(parts)


@mcp.tool()
async def format_citation(reference_json: str, style: str = "apa") -> str:
    """Format a reference in a specified citation style (APA, AMA, IEEE, Vancouver).

    Expects reference_json as a JSON string with keys: title, authors (list), year,
    journal, volume, issue, pages, doi.
    """
    try:
        data = json.loads(reference_json)
    except json.JSONDecodeError as e:
        return f"**Error parsing JSON:** {e}"

    ref = Reference(
        doi=data.get("doi", ""),
        title=data.get("title", ""),
        authors=data.get("authors", []),
        year=data.get("year", ""),
        journal=data.get("journal", ""),
        volume=data.get("volume", ""),
        issue=data.get("issue", ""),
        pages=data.get("pages", ""),
        bibtex_key=data.get("bibtex_key", ""),
        entry_type=data.get("entry_type", "article"),
    )

    style = style.lower().strip()
    formatters = {
        "apa": _format_apa,
        "ama": _format_ama,
        "ieee": _format_ieee,
        "vancouver": _format_vancouver,
    }

    formatter = formatters.get(style)
    if not formatter:
        return f"**Error:** Unknown style `{style}`. Supported: APA, AMA, IEEE, Vancouver."

    formatted = formatter(ref)
    return f"## Citation ({style.upper()})\n\n{formatted}\n"


def _format_author_apa(name: str) -> str:
    """Format 'Family, Given' as 'Family, G.' for APA."""
    parts = [p.strip() for p in name.split(",", 1)]
    if len(parts) == 2 and parts[1]:
        initials = ". ".join(w[0] for w in parts[1].split() if w) + "."
        return f"{parts[0]}, {initials}"
    return parts[0]


def _format_apa(ref: Reference) -> str:
    """APA 7th edition style."""
    authors = [_format_author_apa(a) for a in ref.authors]
    if len(authors) > 1:
        author_str = ", ".join(authors[:-1]) + ", & " + authors[-1]
    elif authors:
        author_str = authors[0]
    else:
        author_str = "Unknown"

    year_part = f" ({ref.year})" if ref.year else ""
    citation = f"{author_str}{year_part}. {ref.title}."

    if ref.journal:
        citation += f" *{ref.journal}*"
        if ref.volume:
            citation += f", *{ref.volume}*"
            if ref.issue:
                citation += f"({ref.issue})"
        if ref.pages:
            citation += f", {ref.pages}"
        citation += "."

    if ref.doi:
        citation += f" https://doi.org/{ref.doi}"

    return citation


def _format_ama(ref: Reference) -> str:
    """AMA (American Medical Association) style."""
    # AMA uses "Family AB" (initials without periods)
    authors: list[str] = []
    for a in ref.authors:
        parts = [p.strip() for p in a.split(",", 1)]
        if len(parts) == 2 and parts[1]:
            initials = "".join(w[0] for w in parts[1].split() if w)
            authors.append(f"{parts[0]} {initials}")
        else:
            authors.append(parts[0])

    author_str = ", ".join(authors) if authors else "Unknown"

    citation = f"{author_str}. {ref.title}."
    if ref.journal:
        citation += f" *{ref.journal}*."
        if ref.year:
            citation += f" {ref.year}"
        if ref.volume:
            citation += f";{ref.volume}"
            if ref.issue:
                citation += f"({ref.issue})"
        if ref.pages:
            citation += f":{ref.pages}"
        citation += "."

    if ref.doi:
        citation += f" doi:{ref.doi}"

    return citation


def _format_ieee(ref: Reference) -> str:
    """IEEE style."""
    # IEEE uses "G. Family" format with initials first
    authors: list[str] = []
    for a in ref.authors:
        parts = [p.strip() for p in a.split(",", 1)]
        if len(parts) == 2 and parts[1]:
            initials = ". ".join(w[0] for w in parts[1].split() if w) + "."
            authors.append(f"{initials} {parts[0]}")
        else:
            authors.append(parts[0])

    if len(authors) > 1:
        author_str = ", ".join(authors[:-1]) + ", and " + authors[-1]
    elif authors:
        author_str = authors[0]
    else:
        author_str = "Unknown"

    citation = f'{author_str}, "{ref.title},"'
    if ref.journal:
        citation += f" *{ref.journal}*"
        if ref.volume:
            citation += f", vol. {ref.volume}"
        if ref.issue:
            citation += f", no. {ref.issue}"
        if ref.pages:
            citation += f", pp. {ref.pages}"
        if ref.year:
            citation += f", {ref.year}"
        citation += "."

    if ref.doi:
        citation += f" doi: {ref.doi}."

    return citation


def _format_vancouver(ref: Reference) -> str:
    """Vancouver style."""
    # Vancouver uses "Family AB" (same as AMA)
    authors: list[str] = []
    for a in ref.authors:
        parts = [p.strip() for p in a.split(",", 1)]
        if len(parts) == 2 and parts[1]:
            initials = "".join(w[0] for w in parts[1].split() if w)
            authors.append(f"{parts[0]} {initials}")
        else:
            authors.append(parts[0])

    author_str = ", ".join(authors) if authors else "Unknown"

    citation = f"{author_str}. {ref.title}."
    if ref.journal:
        citation += f" {ref.journal}."
        if ref.year:
            citation += f" {ref.year}"
        if ref.volume:
            citation += f";{ref.volume}"
            if ref.issue:
                citation += f"({ref.issue})"
        if ref.pages:
            citation += f":{ref.pages}"
        citation += "."

    return citation


@mcp.tool()
async def check_references(manuscript_path: str, bibtex_path: str) -> str:
    """Check manuscript citations against a BibTeX bibliography file.

    Reads the manuscript, finds citation keys (e.g. \\cite{key}), and cross-checks
    against the .bib file. Reports missing and unused references.
    """
    ms_path = Path(manuscript_path)
    bib_path = Path(bibtex_path)

    if not ms_path.exists():
        return f"**Error:** Manuscript not found: `{manuscript_path}`"
    if not bib_path.exists():
        return f"**Error:** BibTeX file not found: `{bibtex_path}`"

    try:
        ms_text = ms_path.read_text(encoding="utf-8", errors="replace")
        bib_text = bib_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"**Error reading files:** {e}"

    # Extract citation keys from manuscript
    # Matches \cite{key1,key2}, \citep{key}, \citet{key}, \autocite{key}, etc.
    cite_pattern = re.compile(r"\\(?:cite[tp]?|autocite|textcite|parencite)\{([^}]+)\}")
    cited_keys: set[str] = set()
    for match in cite_pattern.finditer(ms_text):
        keys = match.group(1)
        for key in keys.split(","):
            key = key.strip()
            if key:
                cited_keys.add(key)

    # Parse bib file to get defined keys
    refs = parse_bibtex(bib_text)
    bib_keys = {ref.bibtex_key for ref in refs}

    # Find discrepancies
    missing_from_bib = sorted(cited_keys - bib_keys)
    unused_in_bib = sorted(bib_keys - cited_keys)

    # Build report
    parts = [
        "## Reference Check Report\n",
        f"- **Manuscript:** `{ms_path.name}`",
        f"- **Bibliography:** `{bib_path.name}`",
        f"- **Citations found in manuscript:** {len(cited_keys)}",
        f"- **Entries in bibliography:** {len(bib_keys)}\n",
    ]

    if missing_from_bib:
        parts.append(f"### Missing from bibliography ({len(missing_from_bib)})\n")
        parts.append("These keys are cited in the manuscript but not defined in the .bib file:\n")
        for key in missing_from_bib:
            parts.append(f"- `{key}`")
        parts.append("")

    if unused_in_bib:
        parts.append(f"### Unused bibliography entries ({len(unused_in_bib)})\n")
        parts.append("These entries exist in the .bib file but are not cited in the manuscript:\n")
        for key in unused_in_bib:
            parts.append(f"- `{key}`")
        parts.append("")

    if not missing_from_bib and not unused_in_bib:
        parts.append("### All clear\n")
        parts.append("All cited keys are present in the bibliography and all bibliography entries are cited.")

    return "\n".join(parts)


if __name__ == "__main__":
    mcp.run()
