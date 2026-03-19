"""arXiv API for preprint search and retrieval MCP Server."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("arxiv-mcp")


@mcp.tool()
async def search_arxiv(query: str, category: str = "", max_results: int = 20) -> str:
    """Search arXiv preprints."""
    raise NotImplementedError("search_arxiv not yet implemented")


@mcp.tool()
async def get_paper(arxiv_id: str) -> str:
    """Get paper metadata and abstract by arXiv ID."""
    raise NotImplementedError("get_paper not yet implemented")


@mcp.tool()
async def get_latex_source(arxiv_id: str) -> str:
    """Download LaTeX source for a paper."""
    raise NotImplementedError("get_latex_source not yet implemented")


if __name__ == "__main__":
    mcp.run()
