"""Journal profile data models."""

from dataclasses import dataclass, field


@dataclass
class FigureRequirements:
    formats: list[str] = field(default_factory=list)
    min_resolution_dpi: int | None = None
    max_count: int | None = None
    max_file_size_mb: float | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class WordLimits:
    abstract: int | None = None
    manuscript: int | None = None
    title: int | None = None
    keywords_count: int | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class FormattingRules:
    font_family: str | None = None
    font_size_pt: float | None = None
    line_spacing: float | None = None
    margins_inches: dict[str, float] = field(default_factory=dict)
    page_size: str | None = None
    columns: int | None = None
    heading_styles: list[dict[str, str]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class JournalProfile:
    name: str
    formatting: FormattingRules = field(default_factory=FormattingRules)
    sections: list[str] = field(default_factory=list)
    citation_style: str | None = None
    word_limits: WordLimits = field(default_factory=WordLimits)
    figure_requirements: FigureRequirements = field(default_factory=FigureRequirements)
    bibliography_style: str | None = None
    document_class: str | None = None
    packages: list[str] = field(default_factory=list)
    extra: dict[str, str] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Render the journal profile as structured markdown."""
        parts: list[str] = []
        parts.append(f"# Journal Profile: {self.name}\n")

        # Formatting rules
        fmt = self.formatting
        parts.append("## Formatting Rules\n")
        if fmt.font_family:
            parts.append(f"- **Font:** {fmt.font_family}")
        if fmt.font_size_pt is not None:
            parts.append(f"- **Font Size:** {fmt.font_size_pt} pt")
        if fmt.line_spacing is not None:
            parts.append(f"- **Line Spacing:** {fmt.line_spacing}")
        if fmt.columns is not None:
            parts.append(f"- **Columns:** {fmt.columns}")
        if fmt.page_size:
            parts.append(f"- **Page Size:** {fmt.page_size}")
        if fmt.margins_inches:
            margin_parts = [f"{k}: {v}\"" for k, v in fmt.margins_inches.items()]
            parts.append(f"- **Margins:** {', '.join(margin_parts)}")
        if fmt.heading_styles:
            parts.append("\n### Heading Styles\n")
            for hs in fmt.heading_styles:
                items = [f"{k}: {v}" for k, v in hs.items()]
                parts.append(f"- {', '.join(items)}")
        if fmt.notes:
            parts.append("\n### Formatting Notes\n")
            for note in fmt.notes:
                parts.append(f"- {note}")
        parts.append("")

        # Sections
        if self.sections:
            parts.append("## Required Sections\n")
            for i, section in enumerate(self.sections, 1):
                parts.append(f"{i}. {section}")
            parts.append("")

        # Citation / bibliography
        if self.citation_style or self.bibliography_style:
            parts.append("## Citation Style\n")
            if self.citation_style:
                parts.append(f"- **Style:** {self.citation_style}")
            if self.bibliography_style:
                parts.append(f"- **Bibliography:** {self.bibliography_style}")
            parts.append("")

        # Word limits
        wl = self.word_limits
        if any([wl.abstract, wl.manuscript, wl.title, wl.keywords_count, wl.notes]):
            parts.append("## Word Limits\n")
            if wl.title is not None:
                parts.append(f"- **Title:** {wl.title} words")
            if wl.abstract is not None:
                parts.append(f"- **Abstract:** {wl.abstract} words")
            if wl.manuscript is not None:
                parts.append(f"- **Manuscript:** {wl.manuscript} words")
            if wl.keywords_count is not None:
                parts.append(f"- **Keywords:** {wl.keywords_count}")
            if wl.notes:
                for note in wl.notes:
                    parts.append(f"- {note}")
            parts.append("")

        # Figure requirements
        fig = self.figure_requirements
        if any([fig.formats, fig.min_resolution_dpi, fig.max_count, fig.max_file_size_mb, fig.notes]):
            parts.append("## Figure Requirements\n")
            if fig.formats:
                parts.append(f"- **Formats:** {', '.join(fig.formats)}")
            if fig.min_resolution_dpi is not None:
                parts.append(f"- **Min Resolution:** {fig.min_resolution_dpi} DPI")
            if fig.max_count is not None:
                parts.append(f"- **Max Figures:** {fig.max_count}")
            if fig.max_file_size_mb is not None:
                parts.append(f"- **Max File Size:** {fig.max_file_size_mb} MB")
            if fig.notes:
                for note in fig.notes:
                    parts.append(f"- {note}")
            parts.append("")

        # Document class / packages (LaTeX)
        if self.document_class or self.packages:
            parts.append("## LaTeX Details\n")
            if self.document_class:
                parts.append(f"- **Document Class:** {self.document_class}")
            if self.packages:
                parts.append(f"- **Packages:** {', '.join(self.packages)}")
            parts.append("")

        # Extra metadata
        if self.extra:
            parts.append("## Additional Information\n")
            for k, v in self.extra.items():
                parts.append(f"- **{k}:** {v}")
            parts.append("")

        return "\n".join(parts)
