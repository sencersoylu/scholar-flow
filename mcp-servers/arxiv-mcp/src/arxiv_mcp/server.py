"""arXiv MCP Server — preprint search and retrieval."""

from mcp.server.fastmcp import FastMCP

from arxiv_mcp.client import ArxivClient
from arxiv_mcp.models import SearchResult

mcp = FastMCP("arxiv-mcp")

_client = ArxivClient()


@mcp.tool()
async def search_arxiv(query: str, category: str = "", max_results: int = 20) -> str:
    """Search arXiv preprints by query and optional category.

    Categories include: cs.CL (computation and language), cs.AI (artificial intelligence),
    cs.LG (machine learning), stat.ML, physics, math, q-bio, etc.
    """
    papers, total = await _client.search(query, category=category, max_results=max_results)
    if not papers:
        return f"No results found for: {query}" + (f" in category {category}" if category else "")

    result = SearchResult(
        query=f"{query}" + (f" [cat:{category}]" if category else ""),
        total_count=total,
        returned_count=len(papers),
        papers=papers,
    )
    return result.to_markdown()


@mcp.tool()
async def get_paper(arxiv_id: str) -> str:
    """Get detailed paper information by arXiv ID (e.g., '2401.12345').

    Returns title, authors, abstract, categories, and links.
    """
    paper = await _client.get_paper(arxiv_id)
    if not paper:
        return f"No paper found with arXiv ID: {arxiv_id}"
    return paper.to_markdown()


@mcp.tool()
async def get_latex_source(arxiv_id: str) -> str:
    """Get the URL for downloading LaTeX source of a paper.

    Returns a download URL. Note: not all papers have LaTeX source available.
    """
    url = await _client.get_latex_source_url(arxiv_id)
    return f"LaTeX source download URL for {arxiv_id}: {url}\n\nUse `fetch` to download if needed."


if __name__ == "__main__":
    mcp.run()
