"""Submission package builder: collect and organize files for journal submission."""

from __future__ import annotations

import shutil
from pathlib import Path


# Files and directories to look for in a project
_MANUSCRIPT_PATTERNS = ["manuscript.md", "manuscript.docx", "manuscript.tex", "main.md", "main.tex", "paper.md", "paper.tex"]
_FIGURE_DIRS = ["figures", "figs", "images"]
_REFERENCE_FILES = ["references.bib", "bibliography.bib", "refs.bib"]
_COVER_LETTER_FILES = ["cover_letter.md", "cover_letter.docx", "cover_letter.txt", "cover-letter.md"]
_SUPPLEMENTARY_DIRS = ["supplementary", "supplements", "appendix"]
_SUPPLEMENTARY_FILES = ["supplementary.md", "supplementary.docx", "supplementary.tex"]


def build_package(project_dir: str, output_dir: str) -> str:
    """Build a structured submission package from a project directory.

    Collects manuscript, figures, references, cover letter, and supplementary
    materials into a clean output directory. Generates a submission checklist.

    Args:
        project_dir: Path to the source project directory.
        output_dir: Path for the structured output package.

    Returns:
        Markdown report of the package contents and checklist.
    """
    project = Path(project_dir)
    output = Path(output_dir)

    if not project.exists():
        raise FileNotFoundError(f"Project directory not found: {project_dir}")

    output.mkdir(parents=True, exist_ok=True)

    report_parts: list[str] = ["# Submission Package Report", ""]
    included: list[str] = []
    missing_items: list[str] = []

    # 1. Manuscript
    manuscript_found = _find_and_copy_file(project, _MANUSCRIPT_PATTERNS, output / "manuscript")
    if manuscript_found:
        included.append(f"Manuscript: `{manuscript_found}`")
    else:
        missing_items.append("Manuscript (no manuscript.md, main.md, or paper.md found)")

    # 2. Figures
    figures_found = _find_and_copy_dir(project, _FIGURE_DIRS, output / "figures")
    if figures_found:
        fig_count = len(list((output / "figures").rglob("*")))
        included.append(f"Figures: {fig_count} file(s) from `{figures_found}`")
    else:
        missing_items.append("Figures directory")

    # 3. References
    refs_found = _find_and_copy_file(project, _REFERENCE_FILES, output)
    if refs_found:
        included.append(f"References: `{refs_found}`")
    else:
        missing_items.append("Bibliography file (.bib)")

    # 4. Cover letter
    cover_found = _find_and_copy_file(project, _COVER_LETTER_FILES, output)
    if cover_found:
        included.append(f"Cover letter: `{cover_found}`")
    else:
        missing_items.append("Cover letter")

    # 5. Supplementary materials
    supp_dir_found = _find_and_copy_dir(project, _SUPPLEMENTARY_DIRS, output / "supplementary")
    supp_file_found = _find_and_copy_file(project, _SUPPLEMENTARY_FILES, output / "supplementary")
    if supp_dir_found or supp_file_found:
        included.append("Supplementary materials")
    else:
        missing_items.append("Supplementary materials")

    # Build report
    report_parts.append("## Included")
    if included:
        for item in included:
            report_parts.append(f"- [x] {item}")
    else:
        report_parts.append("- No files found")

    report_parts.append("")
    report_parts.append("## Missing")
    if missing_items:
        for item in missing_items:
            report_parts.append(f"- [ ] {item}")
    else:
        report_parts.append("- All components present!")

    report_parts.append("")
    report_parts.append("## Submission Checklist")
    report_parts.append(f"- [{'x' if manuscript_found else ' '}] Manuscript file")
    report_parts.append(f"- [{'x' if figures_found else ' '}] Figures")
    report_parts.append(f"- [{'x' if refs_found else ' '}] References / Bibliography")
    report_parts.append(f"- [{'x' if cover_found else ' '}] Cover letter")
    report_parts.append(f"- [{'x' if supp_dir_found or supp_file_found else ' '}] Supplementary materials")
    report_parts.append(f"- [ ] Final proofreading")
    report_parts.append(f"- [ ] Co-author approval")

    report_parts.append("")
    report_parts.append(f"**Package directory:** `{output}`")

    return "\n".join(report_parts)


def _find_and_copy_file(
    project: Path, patterns: list[str], dest: Path
) -> str | None:
    """Search for a file matching any pattern and copy it to dest."""
    for pattern in patterns:
        source = project / pattern
        if source.exists():
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / source.name if dest.is_dir() or not dest.suffix else dest
            if dest.suffix:
                # dest is a directory stem like "manuscript" — use parent
                dest.parent.mkdir(parents=True, exist_ok=True)
                target = dest.parent / source.name
            shutil.copy2(source, target)
            return source.name
    return None


def _find_and_copy_dir(
    project: Path, dir_names: list[str], dest: Path
) -> str | None:
    """Search for a directory matching any name and copy it to dest."""
    for name in dir_names:
        source = project / name
        if source.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
            return name
    return None
