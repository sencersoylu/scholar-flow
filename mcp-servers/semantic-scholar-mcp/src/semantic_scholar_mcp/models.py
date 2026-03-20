"""Semantic Scholar data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Author:
    authorId: str
    name: str
    paperCount: int = 0
    citationCount: int = 0
    hIndex: int = 0

    def to_markdown(self) -> str:
        return (
            f"## {self.name}\n\n"
            f"- **Author ID:** {self.authorId}\n"
            f"- **Papers:** {self.paperCount}\n"
            f"- **Citations:** {self.citationCount}\n"
            f"- **h-index:** {self.hIndex}\n"
        )


@dataclass
class Paper:
    paperId: str
    title: str
    authors: list[dict] = field(default_factory=list)
    year: int | None = None
    abstract: str | None = None
    citationCount: int = 0
    referenceCount: int = 0
    venue: str = ""
    url: str = ""
    externalIds: dict = field(default_factory=dict)
    fieldsOfStudy: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        authors_str = ", ".join(a.get("name", "Unknown") for a in self.authors) if self.authors else "N/A"
        year_str = str(self.year) if self.year else "N/A"
        abstract_str = self.abstract if self.abstract else "N/A"
        venue_str = self.venue if self.venue else "N/A"
        fields_str = ", ".join(self.fieldsOfStudy) if self.fieldsOfStudy else "N/A"

        doi = self.externalIds.get("DOI", "")
        doi_str = f"https://doi.org/{doi}" if doi else "N/A"
        arxiv = self.externalIds.get("ArXiv", "")
        arxiv_str = f"https://arxiv.org/abs/{arxiv}" if arxiv else "N/A"

        return (
            f"### {self.title}\n\n"
            f"- **Authors:** {authors_str}\n"
            f"- **Year:** {year_str}\n"
            f"- **Venue:** {venue_str}\n"
            f"- **Citations:** {self.citationCount} | **References:** {self.referenceCount}\n"
            f"- **DOI:** {doi_str}\n"
            f"- **ArXiv:** {arxiv_str}\n"
            f"- **Fields:** {fields_str}\n"
            f"- **Semantic Scholar:** {self.url}\n\n"
            f"**Abstract:** {abstract_str}\n"
        )


@dataclass
class SearchResult:
    query: str
    total: int
    offset: int
    papers: list[Paper]

    def to_markdown(self) -> str:
        header = (
            f'## Semantic Scholar Search: "{self.query}"\n\n'
            f"Found {self.total} results, showing {len(self.papers)}.\n\n"
        )
        papers_md = "\n---\n\n".join(p.to_markdown() for p in self.papers)
        return header + papers_md
