"""Figure placement: insert images at marked positions in manuscripts."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document
from docx.shared import Inches


def place_figures(
    manuscript_path: str, figures_dir: str, output_path: str | None = None
) -> str:
    """Replace figure markers in a manuscript with actual images.

    Supports two marker formats:
    - [FIGURE:filename.png] — simple marker with optional caption after colon
    - ![caption](path) — standard markdown image syntax

    For .docx files, images are inserted inline.
    For .md files, markers are resolved to absolute paths.

    Args:
        manuscript_path: Path to the manuscript (.docx or .md).
        figures_dir: Directory containing figure image files.
        output_path: Optional output path. If None, overwrites the input.

    Returns:
        The output path of the manuscript with figures placed.
    """
    manuscript_path = Path(manuscript_path)
    figures_dir = Path(figures_dir)

    if not manuscript_path.exists():
        raise FileNotFoundError(f"Manuscript not found: {manuscript_path}")
    if not figures_dir.exists():
        raise FileNotFoundError(f"Figures directory not found: {figures_dir}")

    if output_path is None:
        output_path = manuscript_path
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    suffix = manuscript_path.suffix.lower()

    if suffix == ".docx":
        return _place_figures_docx(manuscript_path, figures_dir, output_path)
    elif suffix == ".md":
        return _place_figures_markdown(manuscript_path, figures_dir, output_path)
    else:
        raise ValueError(f"Unsupported manuscript format: {suffix}. Use .docx or .md")


def _find_figure(figures_dir: Path, filename: str) -> Path | None:
    """Find a figure file in the figures directory."""
    # Try exact match first
    candidate = figures_dir / filename
    if candidate.exists():
        return candidate

    # Try case-insensitive match
    for f in figures_dir.iterdir():
        if f.name.lower() == filename.lower():
            return f

    return None


def _place_figures_docx(
    manuscript_path: Path, figures_dir: Path, output_path: Path
) -> str:
    """Place figures in a Word document."""
    doc = Document(str(manuscript_path))
    placed = []
    missing = []

    for para in doc.paragraphs:
        text = para.text.strip()

        # Check for [FIGURE:filename] marker
        figure_match = re.match(r"^\[FIGURE:(.+?)\]$", text)
        if figure_match:
            filename = figure_match.group(1).strip()
            fig_path = _find_figure(figures_dir, filename)
            if fig_path:
                para.clear()
                run = para.add_run()
                run.add_picture(str(fig_path), width=Inches(5))
                placed.append(filename)
            else:
                missing.append(filename)
            continue

        # Check for ![caption](path) marker
        img_match = re.match(r"^!\[([^\]]*)\]\((.+?)\)$", text)
        if img_match:
            caption = img_match.group(1)
            img_ref = img_match.group(2)
            filename = Path(img_ref).name
            fig_path = _find_figure(figures_dir, filename)
            if fig_path:
                para.clear()
                run = para.add_run()
                run.add_picture(str(fig_path), width=Inches(5))
                if caption:
                    cap_para = doc.add_paragraph()
                    cap_run = cap_para.add_run(f"Figure: {caption}")
                    cap_run.italic = True
                placed.append(filename)
            else:
                missing.append(filename)

    doc.save(str(output_path))
    return str(output_path)


def _place_figures_markdown(
    manuscript_path: Path, figures_dir: Path, output_path: Path
) -> str:
    """Place figures in a markdown file by resolving paths."""
    content = manuscript_path.read_text(encoding="utf-8")
    placed = []
    missing = []

    def replace_figure_marker(match: re.Match) -> str:
        filename = match.group(1).strip()
        fig_path = _find_figure(figures_dir, filename)
        if fig_path:
            placed.append(filename)
            return f"![{filename}]({fig_path})"
        missing.append(filename)
        return match.group(0)  # leave as-is

    def replace_img_marker(match: re.Match) -> str:
        caption = match.group(1)
        img_ref = match.group(2)
        filename = Path(img_ref).name
        fig_path = _find_figure(figures_dir, filename)
        if fig_path:
            placed.append(filename)
            return f"![{caption}]({fig_path})"
        missing.append(filename)
        return match.group(0)

    content = re.sub(r"\[FIGURE:(.+?)\]", replace_figure_marker, content)
    content = re.sub(r"!\[([^\]]*)\]\((.+?)\)", replace_img_marker, content)

    output_path.write_text(content, encoding="utf-8")
    return str(output_path)
