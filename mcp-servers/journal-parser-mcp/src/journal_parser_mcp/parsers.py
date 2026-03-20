"""Parsing utilities for journal templates and author guidelines."""

import re
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, Emu

from journal_parser_mcp.models import (
    FigureRequirements,
    FormattingRules,
    JournalProfile,
    WordLimits,
)


# ---------------------------------------------------------------------------
# DOCX parsing
# ---------------------------------------------------------------------------

def _emu_to_inches(emu: int | None) -> float | None:
    """Convert EMU (English Metric Units) to inches."""
    if emu is None:
        return None
    return round(emu / 914400, 2)


def _pt_value(pt_obj) -> float | None:
    """Safely extract point value from a Pt-like object."""
    if pt_obj is None:
        return None
    try:
        return round(float(pt_obj.pt), 1)
    except (AttributeError, TypeError):
        return None


def parse_docx(file_path: str) -> JournalProfile:
    """Parse a .docx template and extract formatting rules.

    Extracts document structure, font sizes, margins, line spacing,
    section order, and page layout.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".docx":
        raise ValueError(f"Expected .docx file, got: {path.suffix}")

    doc = Document(str(path))

    # --- Page layout from first section ---
    section = doc.sections[0] if doc.sections else None
    margins: dict[str, float] = {}
    page_size: str | None = None

    if section is not None:
        for side in ("top", "bottom", "left", "right"):
            val = _emu_to_inches(getattr(section, f"{side}_margin", None))
            if val is not None:
                margins[side] = val

        width_in = _emu_to_inches(getattr(section, "page_width", None))
        height_in = _emu_to_inches(getattr(section, "page_height", None))
        if width_in and height_in:
            # Detect common page sizes
            if abs(width_in - 8.5) < 0.2 and abs(height_in - 11.0) < 0.2:
                page_size = "Letter (8.5\" x 11\")"
            elif abs(width_in - 8.27) < 0.2 and abs(height_in - 11.69) < 0.2:
                page_size = "A4 (8.27\" x 11.69\")"
            else:
                page_size = f"{width_in}\" x {height_in}\""

    # --- Heading styles and sections ---
    heading_styles: list[dict[str, str]] = []
    sections_found: list[str] = []
    seen_heading_levels: set[str] = set()

    font_family: str | None = None
    font_size_pt: float | None = None
    line_spacing_val: float | None = None

    for para in doc.paragraphs:
        style = para.style

        # Detect headings
        if style and style.name and style.name.startswith("Heading"):
            level = style.name.replace("Heading", "").strip()
            text = para.text.strip()
            if text:
                sections_found.append(text)

            # Collect unique heading style info
            if level and level not in seen_heading_levels:
                seen_heading_levels.add(level)
                hs: dict[str, str] = {"level": level}
                # Check paragraph-level font overrides
                if para.runs:
                    run = para.runs[0]
                    if run.font.size:
                        hs["font_size"] = f"{_pt_value(run.font.size)} pt"
                    if run.font.name:
                        hs["font"] = run.font.name
                    if run.bold:
                        hs["bold"] = "yes"
                    if run.italic:
                        hs["italic"] = "yes"
                heading_styles.append(hs)

        # Extract body text formatting from Normal style paragraphs
        if style and style.name == "Normal" and para.text.strip():
            if font_family is None and para.runs:
                run = para.runs[0]
                if run.font.name:
                    font_family = run.font.name
                if run.font.size:
                    font_size_pt = _pt_value(run.font.size)
            if line_spacing_val is None and para.paragraph_format.line_spacing is not None:
                try:
                    ls = float(para.paragraph_format.line_spacing)
                    # Values < 4 are multipliers (1.0, 1.5, 2.0); larger values are Pt
                    if ls < 4:
                        line_spacing_val = ls
                    else:
                        line_spacing_val = round(ls / 12.0, 1)  # rough Pt→multiplier
                except (TypeError, ValueError):
                    pass

    # Fall back to default style font info
    if font_family is None:
        default_font = doc.styles["Normal"].font if "Normal" in doc.styles else None
        if default_font:
            font_family = default_font.name
            if default_font.size and font_size_pt is None:
                font_size_pt = _pt_value(default_font.size)

    formatting = FormattingRules(
        font_family=font_family,
        font_size_pt=font_size_pt,
        line_spacing=line_spacing_val,
        margins_inches=margins,
        page_size=page_size,
        heading_styles=heading_styles,
    )

    name = path.stem.replace("_", " ").replace("-", " ").title()

    return JournalProfile(
        name=name,
        formatting=formatting,
        sections=sections_found,
    )


# ---------------------------------------------------------------------------
# LaTeX parsing
# ---------------------------------------------------------------------------

def parse_latex(file_path: str) -> JournalProfile:
    """Parse a LaTeX file (.tex, .cls, .sty) and extract formatting rules.

    Extracts document class, packages, section structure, column layout,
    font settings, and bibliography style.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() not in (".tex", ".cls", ".sty"):
        raise ValueError(f"Expected .tex, .cls, or .sty file, got: {path.suffix}")

    content = path.read_text(encoding="utf-8", errors="replace")

    # Document class
    doc_class: str | None = None
    doc_class_match = re.search(r"\\documentclass(?:\[([^\]]*)\])?\{([^}]+)\}", content)
    doc_class_options: str | None = None
    if doc_class_match:
        doc_class_options = doc_class_match.group(1)
        doc_class = doc_class_match.group(2)

    # Packages
    packages: list[str] = re.findall(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", content)
    # Flatten comma-separated packages
    flat_packages: list[str] = []
    for pkg in packages:
        flat_packages.extend(p.strip() for p in pkg.split(",") if p.strip())

    # Section structure
    section_cmds = re.findall(
        r"\\(section|subsection|subsubsection)\*?\{([^}]+)\}", content
    )
    sections = [name for _, name in section_cmds]

    # Column layout
    columns: int | None = None
    if doc_class_options and "twocolumn" in doc_class_options:
        columns = 2
    elif "\\twocolumn" in content:
        columns = 2
    elif doc_class_options and "onecolumn" in doc_class_options:
        columns = 1
    elif "\\onecolumn" in content:
        columns = 1

    # Font size from document class options
    font_size_pt: float | None = None
    if doc_class_options:
        size_match = re.search(r"(\d+)pt", doc_class_options)
        if size_match:
            font_size_pt = float(size_match.group(1))

    # Font package detection
    font_family: str | None = None
    font_map = {
        "times": "Times New Roman",
        "newtxtext": "Times New Roman",
        "mathptmx": "Times New Roman",
        "helvet": "Helvetica",
        "courier": "Courier",
        "palatino": "Palatino",
        "newpxtext": "Palatino",
        "lmodern": "Latin Modern",
        "libertine": "Linux Libertine",
    }
    for pkg_name, font_name in font_map.items():
        if pkg_name in flat_packages:
            font_family = font_name
            break

    # Line spacing
    line_spacing: float | None = None
    spacing_match = re.search(r"\\(?:setstretch|linespread)\{([^}]+)\}", content)
    if spacing_match:
        try:
            line_spacing = float(spacing_match.group(1))
        except ValueError:
            pass
    if line_spacing is None and "\\doublespacing" in content:
        line_spacing = 2.0
    elif line_spacing is None and "\\onehalfspacing" in content:
        line_spacing = 1.5

    # Bibliography style
    bib_style: str | None = None
    bib_match = re.search(r"\\bibliographystyle\{([^}]+)\}", content)
    if bib_match:
        bib_style = bib_match.group(1)

    # Citation style heuristic
    citation_style: str | None = None
    if "natbib" in flat_packages:
        # Check for numbers option
        natbib_match = re.search(r"\\usepackage\[([^\]]*)\]\{natbib\}", content)
        if natbib_match and "numbers" in natbib_match.group(1):
            citation_style = "numbered (natbib)"
        else:
            citation_style = "author-year (natbib)"
    elif "biblatex" in flat_packages:
        biblatex_match = re.search(r"\\usepackage\[([^\]]*)\]\{biblatex\}", content)
        if biblatex_match:
            opts = biblatex_match.group(1)
            style_m = re.search(r"style=([^,\]]+)", opts)
            if style_m:
                citation_style = f"{style_m.group(1)} (biblatex)"
            else:
                citation_style = "biblatex"
        else:
            citation_style = "biblatex"
    elif "\\cite{" in content or "\\cite[" in content:
        citation_style = "numbered"

    # Page size from geometry package
    page_size: str | None = None
    geom_match = re.search(r"\\usepackage\[([^\]]*)\]\{geometry\}", content)
    margins: dict[str, float] = {}
    if geom_match:
        geom_opts = geom_match.group(1)
        if "a4paper" in geom_opts:
            page_size = "A4"
        elif "letterpaper" in geom_opts:
            page_size = "Letter"
        for side in ("top", "bottom", "left", "right"):
            m = re.search(rf"{side}\s*=\s*([\d.]+)\s*(in|cm|mm)", geom_opts)
            if m:
                val = float(m.group(1))
                unit = m.group(2)
                if unit == "cm":
                    val = round(val / 2.54, 2)
                elif unit == "mm":
                    val = round(val / 25.4, 2)
                margins[side] = val

    formatting = FormattingRules(
        font_family=font_family,
        font_size_pt=font_size_pt,
        line_spacing=line_spacing,
        margins_inches=margins,
        page_size=page_size,
        columns=columns,
    )

    name = path.stem.replace("_", " ").replace("-", " ").title()

    return JournalProfile(
        name=name,
        formatting=formatting,
        sections=sections,
        citation_style=citation_style,
        bibliography_style=bib_style,
        document_class=doc_class,
        packages=flat_packages,
    )


# ---------------------------------------------------------------------------
# Guidelines text parsing
# ---------------------------------------------------------------------------

def parse_guidelines_text(text: str) -> JournalProfile:
    """Parse unstructured author guidelines text using regex and heuristics.

    Extracts word limits, figure requirements, reference style,
    and section requirements from raw text.
    """
    if not text or not text.strip():
        raise ValueError("Guidelines text is empty")

    word_limits = WordLimits()
    figure_reqs = FigureRequirements()
    sections: list[str] = []
    citation_style: str | None = None

    lower = text.lower()

    # --- Word limits ---
    # Abstract word limit
    abstract_patterns = [
        r"abstract\s*(?:should\s+(?:be|not\s+exceed)|must\s+(?:be|not\s+exceed)|limit(?:ed)?\s+to|of|:)?\s*(?:no\s+more\s+than\s+)?(\d{2,4})\s*words",
        r"(\d{2,4})\s*-?\s*word\s+abstract",
        r"abstract\s*\(\s*(?:max(?:imum)?\s*)?(\d{2,4})\s*words?\s*\)",
    ]
    for pat in abstract_patterns:
        m = re.search(pat, lower)
        if m:
            word_limits.abstract = int(m.group(1))
            break

    # Manuscript word limit
    manuscript_patterns = [
        r"(?:manuscript|main\s+text|body|total)\s*(?:should\s+(?:be|not\s+exceed)|must\s+(?:be|not\s+exceed)|limit(?:ed)?\s+to|of|:)?\s*(?:no\s+more\s+than\s+)?(\d{3,6})\s*words",
        r"(\d{3,6})\s*-?\s*word\s+(?:limit|manuscript|maximum)",
        r"word\s+(?:limit|count)\s*(?:is|:)\s*(\d{3,6})",
        r"(?:not\s+exceed|maximum\s+of|up\s+to)\s+(\d{3,6})\s+words",
    ]
    for pat in manuscript_patterns:
        m = re.search(pat, lower)
        if m:
            val = int(m.group(1))
            # Distinguish from abstract limits (manuscripts are usually > 500)
            if val > 500:
                word_limits.manuscript = val
                break

    # Title word limit
    title_match = re.search(r"title\s*(?:should\s+(?:be|not\s+exceed)|must\s+(?:be|not\s+exceed)|limit(?:ed)?\s+to|of|:)?\s*(?:no\s+more\s+than\s+)?(\d{1,3})\s*words", lower)
    if title_match:
        word_limits.title = int(title_match.group(1))

    # Keywords count
    kw_match = re.search(r"(\d{1,2})\s*(?:to|-)\s*(\d{1,2})\s*keywords", lower)
    if kw_match:
        word_limits.keywords_count = int(kw_match.group(2))
    else:
        kw_match2 = re.search(r"(?:up\s+to|maximum\s+(?:of\s+)?|no\s+more\s+than\s+)(\d{1,2})\s*keywords", lower)
        if kw_match2:
            word_limits.keywords_count = int(kw_match2.group(1))

    # --- Figure requirements ---
    # Formats
    fig_formats: list[str] = []
    for fmt in ("tiff", "tif", "eps", "png", "jpeg", "jpg", "pdf", "svg"):
        if re.search(rf"\b{fmt}\b", lower):
            fig_formats.append(fmt.upper())
    figure_reqs.formats = fig_formats

    # Resolution
    res_match = re.search(r"(\d{3,4})\s*dpi", lower)
    if res_match:
        figure_reqs.min_resolution_dpi = int(res_match.group(1))

    # Max figure count
    fig_count_match = re.search(r"(?:maximum\s+(?:of\s+)?|up\s+to\s+|no\s+more\s+than\s+)(\d{1,2})\s*(?:figures?|illustrations?)", lower)
    if fig_count_match:
        figure_reqs.max_count = int(fig_count_match.group(1))

    # Max file size
    size_match = re.search(r"(\d+(?:\.\d+)?)\s*mb\s*(?:per\s+figure|maximum|limit)?", lower)
    if size_match:
        figure_reqs.max_file_size_mb = float(size_match.group(1))

    # --- Citation / reference style ---
    if re.search(r"\bnumbered\s+referenc", lower) or re.search(r"references?\s+(?:should\s+be\s+)?numbered", lower):
        citation_style = "numbered"
    elif re.search(r"author[\s-]*year", lower):
        citation_style = "author-year"
    elif re.search(r"\bvancouver\b", lower):
        citation_style = "Vancouver (numbered)"
    elif re.search(r"\bapa\b", lower):
        citation_style = "APA (author-year)"
    elif re.search(r"\bharvard\b", lower):
        citation_style = "Harvard (author-year)"
    elif re.search(r"\bchicago\b", lower):
        citation_style = "Chicago"
    elif re.search(r"\bieee\b", lower):
        citation_style = "IEEE (numbered)"

    # --- Section requirements ---
    common_sections = [
        "Abstract", "Introduction", "Methods", "Materials and Methods",
        "Results", "Discussion", "Results and Discussion", "Conclusion",
        "Conclusions", "Acknowledgments", "Acknowledgements", "References",
        "Supplementary Materials", "Supplementary Information",
        "Data Availability", "Conflict of Interest", "Author Contributions",
        "Funding", "Ethics Statement", "Keywords",
    ]
    for sec in common_sections:
        if re.search(rf"\b{re.escape(sec)}\b", text, re.IGNORECASE):
            sections.append(sec)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_sections: list[str] = []
    for s in sections:
        sl = s.lower()
        if sl not in seen:
            seen.add(sl)
            unique_sections.append(s)
    sections = unique_sections

    return JournalProfile(
        name="Parsed Guidelines",
        sections=sections,
        citation_style=citation_style,
        word_limits=word_limits,
        figure_requirements=figure_reqs,
    )
