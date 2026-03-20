#!/usr/bin/env python3
"""Convert DOIs to BibTeX entries via the CrossRef API.

Queries https://api.crossref.org/works/{doi} for each provided DOI and
formats the returned metadata as a BibTeX entry.  Uses only the Python
standard library (urllib, json) so no pip installs are required.

Examples
--------
    # Single DOI to stdout
    python doi_to_bibtex.py --doi 10.1038/s41586-020-2649-2

    # Multiple DOIs written to a file
    python doi_to_bibtex.py --doi 10.1038/s41586-020-2649-2 10.1126/science.abc4346 --output refs.bib
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import urllib.error
import urllib.request
from typing import Any

# ---------------------------------------------------------------------------
# CrossRef helpers
# ---------------------------------------------------------------------------

CROSSREF_API = "https://api.crossref.org/works/{doi}"
USER_AGENT = "scholar-flow-citation-tools/0.1 (mailto:scholarly@example.com)"


def _fetch_crossref(doi: str) -> dict[str, Any]:
    """Return the CrossRef *message* dict for *doi*, or raise on failure."""
    url = CROSSREF_API.format(doi=doi)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise ValueError(f"DOI not found: {doi}") from exc
        raise RuntimeError(
            f"CrossRef returned HTTP {exc.code} for DOI {doi}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Network error while querying CrossRef for DOI {doi}: {exc.reason}"
        ) from exc
    return data.get("message", {})


# ---------------------------------------------------------------------------
# BibTeX formatting
# ---------------------------------------------------------------------------

def _make_cite_key(meta: dict[str, Any]) -> str:
    """Generate a readable citation key like ``AuthorYYYY``."""
    authors = meta.get("author", [])
    if authors:
        family = authors[0].get("family", "Unknown")
        family = re.sub(r"[^A-Za-z]", "", family)
    else:
        family = "Unknown"

    date_parts = meta.get("issued", {}).get("date-parts", [[None]])
    year = date_parts[0][0] if date_parts and date_parts[0] else "XXXX"
    return f"{family}{year}"


def _join_authors(authors: list[dict[str, str]]) -> str:
    """Format a CrossRef author list as a BibTeX ``author`` field value."""
    parts: list[str] = []
    for a in authors:
        given = a.get("given", "")
        family = a.get("family", "")
        if family and given:
            parts.append(f"{family}, {given}")
        elif family:
            parts.append(family)
    return " and ".join(parts)


def _get_pages(meta: dict[str, Any]) -> str:
    """Extract page string, normalising en-dash."""
    page = meta.get("page", "")
    return page.replace("-", "--") if page else ""


def _format_bibtex(meta: dict[str, Any]) -> str:
    """Convert a CrossRef *message* dict into a BibTeX entry string."""
    entry_type = "article"  # default
    cr_type = meta.get("type", "")
    if "book" in cr_type:
        entry_type = "book"
    elif "proceedings" in cr_type or "conference" in cr_type:
        entry_type = "inproceedings"

    cite_key = _make_cite_key(meta)

    fields: list[tuple[str, str]] = []

    # Author
    authors = meta.get("author", [])
    if authors:
        fields.append(("author", _join_authors(authors)))

    # Title
    titles = meta.get("title", [])
    if titles:
        fields.append(("title", "{" + titles[0] + "}"))

    # Journal / container
    containers = meta.get("container-title", [])
    if containers:
        field_name = "journal" if entry_type == "article" else "booktitle"
        fields.append((field_name, containers[0]))

    # Year
    date_parts = meta.get("issued", {}).get("date-parts", [[None]])
    year = date_parts[0][0] if date_parts and date_parts[0] else None
    if year is not None:
        fields.append(("year", str(year)))

    # Month
    if date_parts and date_parts[0] and len(date_parts[0]) >= 2:
        month = date_parts[0][1]
        if month:
            fields.append(("month", str(month)))

    # Volume / issue / pages
    volume = meta.get("volume", "")
    if volume:
        fields.append(("volume", volume))
    issue = meta.get("issue", "")
    if issue:
        fields.append(("number", issue))
    pages = _get_pages(meta)
    if pages:
        fields.append(("pages", pages))

    # DOI
    doi = meta.get("DOI", "")
    if doi:
        fields.append(("doi", doi))

    # Publisher
    publisher = meta.get("publisher", "")
    if publisher:
        fields.append(("publisher", publisher))

    # ISSN
    issns = meta.get("ISSN", [])
    if issns:
        fields.append(("issn", issns[0]))

    # URL
    url = meta.get("URL", "")
    if url:
        fields.append(("url", url))

    # Build the entry text
    max_key_len = max(len(k) for k, _ in fields) if fields else 0
    lines = [f"@{entry_type}{{{cite_key},"]
    for key, value in fields:
        padding = " " * (max_key_len - len(key))
        lines.append(f"  {key}{padding} = {{{value}}},")
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def doi_to_bibtex(doi: str) -> str:
    """Fetch metadata for *doi* from CrossRef and return a BibTeX string.

    Parameters
    ----------
    doi : str
        A DOI such as ``10.1038/s41586-020-2649-2``.

    Returns
    -------
    str
        A formatted BibTeX entry.

    Raises
    ------
    ValueError
        If the DOI is not found (HTTP 404).
    RuntimeError
        On network or unexpected HTTP errors.
    """
    meta = _fetch_crossref(doi)
    return _format_bibtex(meta)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert DOIs to BibTeX entries via the CrossRef API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              %(prog)s --doi 10.1038/s41586-020-2649-2
              %(prog)s --doi 10.1038/s41586-020-2649-2 10.1126/science.abc4346 -o refs.bib
        """),
    )
    parser.add_argument(
        "--doi",
        nargs="+",
        required=True,
        help="One or more DOIs to look up.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path.  Defaults to stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    entries: list[str] = []
    errors: int = 0

    for doi in args.doi:
        doi = doi.strip().strip(",")
        if not doi:
            continue
        try:
            bib = doi_to_bibtex(doi)
            entries.append(bib)
        except (ValueError, RuntimeError) as exc:
            print(f"ERROR [{doi}]: {exc}", file=sys.stderr)
            errors += 1

    output_text = "\n\n".join(entries)
    if output_text:
        output_text += "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output_text)
        print(
            f"Wrote {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} "
            f"to {args.output}",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(output_text)

    return 1 if errors and not entries else (2 if errors else 0)


if __name__ == "__main__":
    raise SystemExit(main())
