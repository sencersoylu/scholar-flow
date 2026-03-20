"""Template and guidelines parsing MCP Server."""

from mcp.server.fastmcp import FastMCP

from journal_parser_mcp.parsers import (
    parse_docx as _parse_docx,
    parse_guidelines_text as _parse_guidelines_text,
    parse_latex as _parse_latex,
)

mcp = FastMCP("journal-parser-mcp")


@mcp.tool()
async def parse_docx_template(file_path: str) -> str:
    """Parse a Word (.docx) journal template to extract formatting rules.

    Extracts document structure, font sizes, margins, line spacing,
    section order, and page layout. Returns a markdown-formatted journal profile.
    """
    try:
        profile = _parse_docx(file_path)
    except FileNotFoundError as e:
        return f"**Error:** {e}"
    except ValueError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error parsing DOCX:** {e}"

    return profile.to_markdown()


@mcp.tool()
async def parse_latex_template(file_path: str) -> str:
    """Parse a LaTeX file (.tex, .cls, .sty) to extract formatting rules.

    Extracts document class, packages, section structure, column layout,
    font settings, and bibliography style. Returns a markdown-formatted journal profile.
    """
    try:
        profile = _parse_latex(file_path)
    except FileNotFoundError as e:
        return f"**Error:** {e}"
    except ValueError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error parsing LaTeX:** {e}"

    return profile.to_markdown()


@mcp.tool()
async def parse_guidelines_text(text: str) -> str:
    """Parse raw author guidelines text to extract submission requirements.

    Extracts word limits, figure requirements, reference style, and section
    requirements using regex and heuristics. Returns a markdown-formatted journal profile.
    """
    try:
        profile = _parse_guidelines_text(text)
    except ValueError as e:
        return f"**Error:** {e}"
    except Exception as e:
        return f"**Error parsing guidelines:** {e}"

    return profile.to_markdown()


if __name__ == "__main__":
    mcp.run()
