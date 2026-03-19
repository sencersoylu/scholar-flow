"""Final document generation via Pandoc MCP Server."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("document-export-mcp")


@mcp.tool()
async def export_docx(markdown_path: str, template_path: str = "", output_path: str = "") -> str:
    """Convert markdown to Word document."""
    raise NotImplementedError("export_docx not yet implemented")


@mcp.tool()
async def export_latex(markdown_path: str, template_path: str = "", output_path: str = "") -> str:
    """Convert markdown to LaTeX."""
    raise NotImplementedError("export_latex not yet implemented")


@mcp.tool()
async def place_figures(manuscript_path: str, figures_dir: str) -> str:
    """Insert figures into manuscript at marked positions."""
    raise NotImplementedError("place_figures not yet implemented")


@mcp.tool()
async def build_submission_package(project_dir: str, output_dir: str) -> str:
    """Build complete submission package."""
    raise NotImplementedError("build_submission_package not yet implemented")


if __name__ == "__main__":
    mcp.run()
