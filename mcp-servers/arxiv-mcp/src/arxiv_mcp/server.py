"""arXiv MCP Server — preprint search and retrieval."""

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from arxiv_mcp.cache import ResponseCache
from arxiv_mcp.client import ArxivClient
from arxiv_mcp.models import SearchResult

mcp = FastMCP("arxiv-mcp")

_client = ArxivClient()
_cache_dir = Path(os.environ.get("SCHOLAR_FLOW_CACHE_DIR", "/tmp/scholar-flow-cache/arxiv"))
_cache = ResponseCache(cache_dir=_cache_dir, ttl_seconds=86400)


@mcp.tool()
async def search_arxiv(query: str, category: str = "", max_results: int = 20) -> str:
    """Search arXiv preprints by query and optional category.

    Categories include: cs.CL (computation and language), cs.AI (artificial intelligence),
    cs.LG (machine learning), stat.ML, physics, math, q-bio, etc.
    """
    cache_key = f"search:{query}:{category}:{max_results}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    papers, total = await _client.search(query, category=category, max_results=max_results)
    if not papers:
        return f"No results found for: {query}" + (f" in category {category}" if category else "")

    result = SearchResult(
        query=f"{query}" + (f" [cat:{category}]" if category else ""),
        total_count=total,
        returned_count=len(papers),
        papers=papers,
    )
    md = result.to_markdown()
    _cache.set(cache_key, {"result": md})
    return md


@mcp.tool()
async def get_paper(arxiv_id: str) -> str:
    """Get detailed paper information by arXiv ID (e.g., '2401.12345').

    Returns title, authors, abstract, categories, and links.
    """
    cache_key = f"paper:{arxiv_id}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    paper = await _client.get_paper(arxiv_id)
    if not paper:
        return f"No paper found with arXiv ID: {arxiv_id}"
    md = paper.to_markdown()
    _cache.set(cache_key, {"result": md})
    return md


@mcp.tool()
async def get_latex_source(arxiv_id: str) -> str:
    """Get the URL for downloading LaTeX source of a paper.

    Returns a download URL. Note: not all papers have LaTeX source available.
    """
    url = await _client.get_latex_source_url(arxiv_id)
    return f"LaTeX source download URL for {arxiv_id}: {url}\n\nUse `fetch` to download if needed."


if __name__ == "__main__":
    mcp.run()
