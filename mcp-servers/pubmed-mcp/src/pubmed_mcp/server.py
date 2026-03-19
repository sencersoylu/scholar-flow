"""PubMed E-utilities API integration MCP Server."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pubmed-mcp")


@mcp.tool()
async def search_pubmed(query: str, max_results: int = 20) -> str:
    """Search PubMed with MeSH term support."""
    raise NotImplementedError("search_pubmed not yet implemented")


@mcp.tool()
async def get_article(pmid: str) -> str:
    """Get article details by PMID."""
    raise NotImplementedError("get_article not yet implemented")


@mcp.tool()
async def search_mesh(term: str) -> str:
    """Search MeSH vocabulary for standardized terms."""
    raise NotImplementedError("search_mesh not yet implemented")


if __name__ == "__main__":
    mcp.run()
