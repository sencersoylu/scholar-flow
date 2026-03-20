"""Document Export MCP Server — convert manuscripts to submission-ready formats."""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from document_export_mcp.converter import markdown_to_docx, markdown_to_latex
from document_export_mcp.figures import place_figures as _place_figures
from document_export_mcp.packager import build_package

mcp = FastMCP("document-export-mcp")


@mcp.tool()
async def export_docx(
    markdown_path: str, template_path: str = "", output_path: str = ""
) -> str:
    """Convert a markdown manuscript to a Word (.docx) document.

    Handles headings, bold/italic formatting, tables, and code blocks.
    Optionally applies styles from a template .docx file.
    """
    try:
        md = Path(markdown_path)
        if not output_path:
            output_path = str(md.with_suffix(".docx"))

        result = markdown_to_docx(
            md_path=markdown_path,
            output_path=output_path,
            template_path=template_path if template_path else None,
        )
        size = Path(result).stat().st_size
        return (
            f"### Export Successful\n\n"
            f"- **Source:** `{markdown_path}`\n"
            f"- **Output:** `{result}`\n"
            f"- **Size:** {size:,} bytes\n"
            f"- **Template:** {'`' + template_path + '`' if template_path else 'Default'}"
        )
    except FileNotFoundError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error exporting to docx:** {e}"


@mcp.tool()
async def export_latex(
    markdown_path: str, template_path: str = "", output_path: str = ""
) -> str:
    """Convert a markdown manuscript to LaTeX (.tex) format.

    Converts headings to \\section/\\subsection, inline formatting to
    \\textbf/\\textit, code blocks to verbatim, and tables to tabular.
    """
    try:
        md = Path(markdown_path)
        if not output_path:
            output_path = str(md.with_suffix(".tex"))

        result = markdown_to_latex(
            md_path=markdown_path,
            output_path=output_path,
            template_path=template_path if template_path else None,
        )
        size = Path(result).stat().st_size
        return (
            f"### Export Successful\n\n"
            f"- **Source:** `{markdown_path}`\n"
            f"- **Output:** `{result}`\n"
            f"- **Size:** {size:,} bytes\n"
            f"- **Template:** {'`' + template_path + '`' if template_path else 'Default (article)'}"
        )
    except FileNotFoundError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error exporting to LaTeX:** {e}"


@mcp.tool()
async def place_figures(manuscript_path: str, figures_dir: str) -> str:
    """Insert figures into a manuscript at marked positions.

    Looks for [FIGURE:filename.png] or ![caption](path) markers and replaces
    them with actual figure insertions. Supports .docx and .md manuscripts.
    """
    try:
        ms = Path(manuscript_path)
        output_path = str(ms.parent / f"{ms.stem}_with_figures{ms.suffix}")

        result = _place_figures(
            manuscript_path=manuscript_path,
            figures_dir=figures_dir,
            output_path=output_path,
        )
        return (
            f"### Figures Placed\n\n"
            f"- **Source:** `{manuscript_path}`\n"
            f"- **Figures from:** `{figures_dir}`\n"
            f"- **Output:** `{result}`"
        )
    except FileNotFoundError as e:
        return f"**Error:** {e}"
    except ValueError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error placing figures:** {e}"


@mcp.tool()
async def build_submission_package(project_dir: str, output_dir: str) -> str:
    """Build a complete submission package from a project directory.

    Collects manuscript, figures, references, cover letter, and supplementary
    materials. Generates a checklist of included and missing components.
    """
    try:
        report = build_package(project_dir=project_dir, output_dir=output_dir)
        return report
    except FileNotFoundError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error building submission package:** {e}"


if __name__ == "__main__":
    mcp.run()
