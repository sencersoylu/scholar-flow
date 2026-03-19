"""Template and guidelines parsing MCP Server."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("journal-parser-mcp")


@mcp.tool()
async def parse_docx_template(file_path: str) -> str:
    """Parse Word template to extract formatting rules."""
    raise NotImplementedError("parse_docx_template not yet implemented")


@mcp.tool()
async def parse_latex_template(file_path: str) -> str:
    """Parse LaTeX cls/sty to extract formatting rules."""
    raise NotImplementedError("parse_latex_template not yet implemented")


@mcp.tool()
async def parse_guidelines_pdf(file_path: str) -> str:
    """Extract author guidelines from PDF."""
    raise NotImplementedError("parse_guidelines_pdf not yet implemented")


if __name__ == "__main__":
    mcp.run()
