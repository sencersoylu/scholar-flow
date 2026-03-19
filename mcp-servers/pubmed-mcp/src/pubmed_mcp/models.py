"""PubMed data models."""

from dataclasses import dataclass, field


@dataclass
class Article:
    pmid: str
    title: str
    authors: list[str]
    journal: str
    year: str
    abstract: str
    doi: str = ""
    mesh_terms: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        authors_str = ", ".join(self.authors)
        mesh_str = ", ".join(self.mesh_terms) if self.mesh_terms else "N/A"
        doi_str = f"https://doi.org/{self.doi}" if self.doi else "N/A"
        return (
            f"### {self.title}\n\n"
            f"- **Authors:** {authors_str}\n"
            f"- **Journal:** {self.journal} ({self.year})\n"
            f"- **PMID:** {self.pmid}\n"
            f"- **DOI:** {doi_str}\n"
            f"- **MeSH Terms:** {mesh_str}\n\n"
            f"**Abstract:** {self.abstract}\n"
        )


@dataclass
class SearchResult:
    query: str
    total_count: int
    returned_count: int
    articles: list[Article]

    def to_markdown(self) -> str:
        header = (
            f"## PubMed Search: \"{self.query}\"\n\n"
            f"Found {self.total_count} results, showing {self.returned_count}.\n\n"
        )
        articles_md = "\n---\n\n".join(a.to_markdown() for a in self.articles)
        return header + articles_md
