"""Citation data models."""

from dataclasses import dataclass, field


@dataclass
class Reference:
    """A bibliographic reference."""

    doi: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    bibtex_key: str = ""
    entry_type: str = "article"

    def to_markdown(self) -> str:
        authors_str = ", ".join(self.authors) if self.authors else "N/A"
        doi_str = f"https://doi.org/{self.doi}" if self.doi else "N/A"
        parts = [
            f"### {self.title}\n",
            f"- **Authors:** {authors_str}",
            f"- **Journal:** {self.journal}" + (f" ({self.year})" if self.year else ""),
            f"- **DOI:** {doi_str}",
        ]
        if self.volume:
            vol = self.volume
            if self.issue:
                vol += f"({self.issue})"
            parts.append(f"- **Volume:** {vol}")
        if self.pages:
            parts.append(f"- **Pages:** {self.pages}")
        parts.append(f"- **BibTeX Key:** {self.bibtex_key}")
        return "\n".join(parts) + "\n"


@dataclass
class ValidationIssue:
    """A single validation issue found in a BibTeX file."""

    severity: str  # "error" or "warning"
    entry_key: str
    message: str

    def to_markdown(self) -> str:
        icon = "ERROR" if self.severity == "error" else "WARNING"
        return f"- **[{icon}]** `{self.entry_key}`: {self.message}"
