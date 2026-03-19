"""PubMed MCP Server — NCBI E-utilities API integration."""

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from pubmed_mcp.cache import ResponseCache
from pubmed_mcp.client import PubMedClient
from pubmed_mcp.models import SearchResult

mcp = FastMCP("pubmed-mcp")

_client = PubMedClient()
_cache_dir = Path(os.environ.get("SCHOLAR_FLOW_CACHE_DIR", "/tmp/scholar-flow-cache/pubmed"))
_cache = ResponseCache(cache_dir=_cache_dir, ttl_seconds=86400)


@mcp.tool()
async def search_pubmed(query: str, max_results: int = 20) -> str:
    """Search PubMed for articles matching a query. Supports MeSH terms.

    Returns formatted markdown with article titles, authors, journals, abstracts, and MeSH terms.
    """
    cache_key = f"search:{query}:{max_results}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    pmids, total = await _client.search(query, max_results=max_results)
    if not pmids:
        return f"No results found for: {query}"

    articles = await _client.fetch_articles(pmids)
    result = SearchResult(
        query=query, total_count=total, returned_count=len(articles), articles=articles
    )
    md = result.to_markdown()
    _cache.set(cache_key, {"result": md})
    return md


@mcp.tool()
async def get_article(pmid: str) -> str:
    """Get detailed article information by PubMed ID (PMID).

    Returns title, authors, journal, abstract, DOI, and MeSH terms.
    """
    cache_key = f"article:{pmid}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    articles = await _client.fetch_articles([pmid])
    if not articles:
        return f"No article found with PMID: {pmid}"
    md = articles[0].to_markdown()
    _cache.set(cache_key, {"result": md})
    return md


@mcp.tool()
async def search_mesh(term: str) -> str:
    """Search MeSH (Medical Subject Headings) vocabulary for standardized terms.

    Use this to find the correct MeSH terms before searching PubMed for more precise results.
    """
    cache_key = f"mesh:{term}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    result = await _client.search_mesh_terms(term)
    _cache.set(cache_key, {"result": result})
    return result


if __name__ == "__main__":
    mcp.run()
