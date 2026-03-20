#!/usr/bin/env python3
"""Extract citation metadata from PubMed IDs via NCBI E-utilities.

Queries the NCBI efetch API for each provided PMID and outputs metadata
in BibTeX, JSON, or human-readable text format.  Uses only the Python
standard library (urllib, xml.etree, json) -- no pip installs required.

Examples
--------
    # Single PMID as BibTeX
    python pubmed_metadata.py --pmid 32284588

    # Multiple PMIDs as JSON
    python pubmed_metadata.py --pmid 32284588 33100345 --format json

    # Write to file
    python pubmed_metadata.py --pmid 32284588 --format bibtex -o refs.bib
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EFETCH_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={pmids}"
)
USER_AGENT = "scholar-flow-citation-tools/0.1"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ArticleMeta:
    """Metadata for a single PubMed article."""

    pmid: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    journal: str = ""
    journal_abbrev: str = ""
    year: str = ""
    month: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str = ""
    pmc: str = ""
    abstract: str = ""


# ---------------------------------------------------------------------------
# XML parsing helpers
# ---------------------------------------------------------------------------


def _text(element: ET.Element | None, path: str, default: str = "") -> str:
    """Safely extract text from an XML element at *path*."""
    if element is None:
        return default
    node = element.find(path)
    if node is None or node.text is None:
        return default
    return node.text.strip()


def _collect_text(element: ET.Element | None, path: str) -> str:
    """Collect all text (including mixed content children) under *path*."""
    if element is None:
        return ""
    node = element.find(path)
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def _parse_article(article_el: ET.Element) -> ArticleMeta:
    """Parse a single <PubmedArticle> element into an ArticleMeta."""
    meta = ArticleMeta()

    # -- PMID --
    medline = article_el.find("MedlineCitation")
    meta.pmid = _text(medline, "PMID")

    article = medline.find("Article") if medline is not None else None

    # -- Title (may contain inline markup) --
    meta.title = _collect_text(article, "ArticleTitle")

    # -- Authors --
    author_list = article.find("AuthorList") if article is not None else None
    if author_list is not None:
        for author_el in author_list.findall("Author"):
            last = _text(author_el, "LastName")
            first = _text(author_el, "ForeName")
            if last and first:
                meta.authors.append(f"{last}, {first}")
            elif last:
                meta.authors.append(last)
            else:
                collective = _text(author_el, "CollectiveName")
                if collective:
                    meta.authors.append(collective)

    # -- Journal --
    journal_el = article.find("Journal") if article is not None else None
    meta.journal = _text(journal_el, "Title")
    meta.journal_abbrev = _text(journal_el, "ISOAbbreviation")

    ji = journal_el.find("JournalIssue") if journal_el is not None else None
    meta.volume = _text(ji, "Volume")
    meta.issue = _text(ji, "Issue")

    # -- Date --
    pub_date = ji.find("PubDate") if ji is not None else None
    meta.year = _text(pub_date, "Year")
    meta.month = _text(pub_date, "Month")
    if not meta.year:
        medline_date = _text(pub_date, "MedlineDate")
        if medline_date:
            m = re.search(r"(\d{4})", medline_date)
            if m:
                meta.year = m.group(1)

    # -- Pages --
    meta.pages = _text(article, "Pagination/MedlinePgn")

    # -- Abstract --
    abstract_el = article.find("Abstract") if article is not None else None
    if abstract_el is not None:
        parts: list[str] = []
        for at in abstract_el.findall("AbstractText"):
            label = at.get("Label", "")
            text = "".join(at.itertext()).strip()
            if label:
                parts.append(f"{label}: {text}")
            else:
                parts.append(text)
        meta.abstract = " ".join(parts)

    # -- DOI / PMC from ArticleIdList --
    pubmed_data = article_el.find("PubmedData")
    id_list = pubmed_data.find("ArticleIdList") if pubmed_data is not None else None
    if id_list is not None:
        for aid in id_list.findall("ArticleId"):
            id_type = aid.get("IdType", "")
            val = (aid.text or "").strip()
            if id_type == "doi":
                meta.doi = val
            elif id_type == "pmc":
                meta.pmc = val

    return meta


# ---------------------------------------------------------------------------
# API interaction
# ---------------------------------------------------------------------------


def fetch_pubmed(pmids: list[str]) -> list[ArticleMeta]:
    """Fetch article metadata from PubMed for the given PMIDs.

    Parameters
    ----------
    pmids : list[str]
        PubMed IDs (numeric strings).

    Returns
    -------
    list[ArticleMeta]
        One entry per successfully fetched article.

    Raises
    ------
    RuntimeError
        On network or HTTP errors.
    """
    joined = ",".join(p.strip() for p in pmids if p.strip())
    if not joined:
        return []

    url = EFETCH_URL.format(pmids=joined)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to reach PubMed: {exc.reason}") from exc

    root = ET.fromstring(raw)
    results: list[ArticleMeta] = []
    for pa in root.findall("PubmedArticle"):
        results.append(_parse_article(pa))
    return results


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def _to_bibtex(meta: ArticleMeta) -> str:
    """Format a single ArticleMeta as a BibTeX @article entry."""
    # Build citation key: FirstAuthorYear
    if meta.authors:
        family = meta.authors[0].split(",")[0]
        family = re.sub(r"[^A-Za-z]", "", family)
    else:
        family = "Unknown"
    key = f"{family}{meta.year or 'XXXX'}"

    fields: list[tuple[str, str]] = []
    if meta.authors:
        fields.append(("author", " and ".join(meta.authors)))
    if meta.title:
        fields.append(("title", "{" + meta.title + "}"))
    if meta.journal:
        fields.append(("journal", meta.journal))
    if meta.year:
        fields.append(("year", meta.year))
    if meta.month:
        fields.append(("month", meta.month))
    if meta.volume:
        fields.append(("volume", meta.volume))
    if meta.issue:
        fields.append(("number", meta.issue))
    if meta.pages:
        fields.append(("pages", meta.pages.replace("-", "--")))
    if meta.doi:
        fields.append(("doi", meta.doi))
    if meta.pmid:
        fields.append(("pmid", meta.pmid))
    if meta.pmc:
        fields.append(("pmcid", meta.pmc))

    max_key_len = max(len(k) for k, _ in fields) if fields else 0
    lines = [f"@article{{{key},"]
    for k, v in fields:
        pad = " " * (max_key_len - len(k))
        lines.append(f"  {k}{pad} = {{{v}}},")
    lines.append("}")
    return "\n".join(lines)


def _to_json(articles: list[ArticleMeta]) -> str:
    """Format a list of ArticleMeta as a JSON array."""
    return json.dumps([asdict(a) for a in articles], indent=2, ensure_ascii=False)


def _to_text(meta: ArticleMeta) -> str:
    """Format a single ArticleMeta as human-readable text."""
    lines: list[str] = []
    lines.append(f"PMID:    {meta.pmid}")
    lines.append(f"Title:   {meta.title}")
    if meta.authors:
        lines.append(f"Authors: {'; '.join(meta.authors)}")
    lines.append(f"Journal: {meta.journal}")
    ref_parts: list[str] = []
    if meta.year:
        ref_parts.append(meta.year)
    if meta.volume:
        vol = meta.volume
        if meta.issue:
            vol += f"({meta.issue})"
        ref_parts.append(vol)
    if meta.pages:
        ref_parts.append(meta.pages)
    if ref_parts:
        lines.append(f"Ref:     {'; '.join(ref_parts)}")
    if meta.doi:
        lines.append(f"DOI:     https://doi.org/{meta.doi}")
    if meta.pmc:
        lines.append(f"PMC:     {meta.pmc}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract citation metadata from PubMed IDs via NCBI E-utilities.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              %(prog)s --pmid 32284588
              %(prog)s --pmid 32284588 33100345 --format json
              %(prog)s --pmid 32284588 --format bibtex -o refs.bib
        """),
    )
    parser.add_argument(
        "--pmid",
        nargs="+",
        required=True,
        help="One or more PubMed IDs to look up.",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["bibtex", "json", "text"],
        default="bibtex",
        help="Output format (default: bibtex).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path.  Defaults to stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        articles = fetch_pubmed(args.pmid)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not articles:
        print("No articles found for the given PMIDs.", file=sys.stderr)
        return 1

    # Format output
    if args.format == "json":
        output_text = _to_json(articles)
    elif args.format == "text":
        output_text = "\n\n".join(_to_text(a) for a in articles)
    else:  # bibtex
        output_text = "\n\n".join(_to_bibtex(a) for a in articles)

    if output_text and not output_text.endswith("\n"):
        output_text += "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output_text)
        print(
            f"Wrote {len(articles)} article(s) to {args.output}",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(output_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
