"""arXiv Atom XML response parser."""

import re
from xml.etree import ElementTree

from arxiv_mcp.models import Paper

ATOM_NS = "http://www.w3.org/2005/Atom"
OPENSEARCH_NS = "http://a9.com/-/spec/opensearch/1.1/"
ARXIV_NS = "http://arxiv.org/schemas/atom"


def _extract_arxiv_id(id_url: str) -> str:
    """Extract arXiv ID from URL like http://arxiv.org/abs/2401.12345v2."""
    match = re.search(r"(\d{4}\.\d{4,5})", id_url)
    return match.group(1) if match else id_url


def parse_search_response(xml_text: str) -> tuple[list[Paper], int]:
    """Parse arXiv Atom feed and return (papers, total_count)."""
    root = ElementTree.fromstring(xml_text)

    total_el = root.find(f"{{{OPENSEARCH_NS}}}totalResults")
    total = int(total_el.text) if total_el is not None and total_el.text else 0

    papers = []
    for entry in root.findall(f"{{{ATOM_NS}}}entry"):
        paper = _parse_entry(entry)
        if paper:
            papers.append(paper)

    return papers, total


def _parse_entry(entry: ElementTree.Element) -> Paper | None:
    id_text = entry.findtext(f"{{{ATOM_NS}}}id", "")
    arxiv_id = _extract_arxiv_id(id_text)

    title = entry.findtext(f"{{{ATOM_NS}}}title", "").strip()
    abstract = entry.findtext(f"{{{ATOM_NS}}}summary", "").strip()
    published = entry.findtext(f"{{{ATOM_NS}}}published", "")[:10]
    updated = entry.findtext(f"{{{ATOM_NS}}}updated", "")[:10]

    authors = []
    for author in entry.findall(f"{{{ATOM_NS}}}author"):
        name = author.findtext(f"{{{ATOM_NS}}}name", "")
        if name:
            authors.append(name)

    categories = []
    for cat in entry.findall(f"{{{ATOM_NS}}}category"):
        term = cat.get("term", "")
        if term:
            categories.append(term)

    doi_el = entry.find(f"{{{ARXIV_NS}}}doi")
    doi = doi_el.text.strip() if doi_el is not None and doi_el.text else ""

    pdf_url = ""
    for link in entry.findall(f"{{{ATOM_NS}}}link"):
        if link.get("title") == "pdf":
            pdf_url = link.get("href", "")
            break

    return Paper(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        abstract=abstract,
        categories=categories,
        published=published,
        updated=updated,
        doi=doi,
        pdf_url=pdf_url,
    )
