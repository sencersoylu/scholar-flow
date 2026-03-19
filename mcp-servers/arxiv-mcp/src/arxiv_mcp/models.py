"""arXiv data models."""

from dataclasses import dataclass


@dataclass
class Paper:
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: str
    updated: str
    doi: str = ""
    pdf_url: str = ""

    def to_markdown(self) -> str:
        authors_str = ", ".join(self.authors)
        cats_str = ", ".join(self.categories)
        doi_str = f"https://doi.org/{self.doi}" if self.doi else "N/A"
        return (
            f"### {self.title}\n\n"
            f"- **arXiv ID:** {self.arxiv_id}\n"
            f"- **Authors:** {authors_str}\n"
            f"- **Categories:** {cats_str}\n"
            f"- **Published:** {self.published}\n"
            f"- **DOI:** {doi_str}\n"
            f"- **PDF:** {self.pdf_url}\n\n"
            f"**Abstract:** {self.abstract}\n"
        )


@dataclass
class SearchResult:
    query: str
    total_count: int
    returned_count: int
    papers: list[Paper]

    def to_markdown(self) -> str:
        header = (
            f'## arXiv Search: "{self.query}"\n\n'
            f"Found {self.total_count} results, showing {self.returned_count}.\n\n"
        )
        papers_md = "\n---\n\n".join(p.to_markdown() for p in self.papers)
        return header + papers_md
