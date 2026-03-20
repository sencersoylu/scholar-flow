"""Semantic Scholar API for citation analysis MCP Server."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from semantic_scholar_mcp.cache import ResponseCache
from semantic_scholar_mcp.client import SemanticScholarClient
from semantic_scholar_mcp.models import SearchResult

mcp = FastMCP("semantic-scholar-mcp")

_client = SemanticScholarClient()
_cache_dir = Path(
    os.environ.get("SCHOLAR_FLOW_CACHE_DIR", "/tmp/scholar-flow-cache/semantic-scholar")
)
_cache = ResponseCache(cache_dir=_cache_dir, ttl_seconds=86400)


@mcp.tool()
async def search_papers(query: str, max_results: int = 20) -> str:
    """Search papers across disciplines using Semantic Scholar.

    Returns formatted markdown with paper titles, authors, venues, abstracts, and citation counts.
    """
    cache_key = f"search:{query}:{max_results}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    papers, total = await _client.search_papers(query, limit=max_results)
    if not papers:
        return f"No results found for: {query}"

    result = SearchResult(query=query, total=total, offset=0, papers=papers)
    md = result.to_markdown()
    _cache.set(cache_key, {"result": md})
    return md


@mcp.tool()
async def get_citations(paper_id: str) -> str:
    """Get papers that cite a given paper.

    Accepts a Semantic Scholar paper ID, DOI, or ArXiv ID.
    Returns formatted markdown list of citing papers.
    """
    cache_key = f"citations:{paper_id}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    papers = await _client.get_citations(paper_id)
    if not papers:
        return f"No citations found for paper: {paper_id}"

    header = f"## Citations for {paper_id}\n\nFound {len(papers)} citing papers.\n\n"
    papers_md = "\n---\n\n".join(p.to_markdown() for p in papers)
    md = header + papers_md
    _cache.set(cache_key, {"result": md})
    return md


@mcp.tool()
async def get_references(paper_id: str) -> str:
    """Get papers referenced by a given paper.

    Accepts a Semantic Scholar paper ID, DOI, or ArXiv ID.
    Returns formatted markdown list of referenced papers.
    """
    cache_key = f"references:{paper_id}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    papers = await _client.get_references(paper_id)
    if not papers:
        return f"No references found for paper: {paper_id}"

    header = f"## References for {paper_id}\n\nFound {len(papers)} referenced papers.\n\n"
    papers_md = "\n---\n\n".join(p.to_markdown() for p in papers)
    md = header + papers_md
    _cache.set(cache_key, {"result": md})
    return md


@mcp.tool()
async def get_author(author_id: str) -> str:
    """Get author profile with h-index and publication stats.

    Accepts a Semantic Scholar author ID.
    Returns formatted markdown with author details.
    """
    cache_key = f"author:{author_id}"
    cached = _cache.get(cache_key)
    if cached:
        return cached["result"]

    author = await _client.get_author(author_id)
    if not author:
        return f"No author found with ID: {author_id}"

    md = author.to_markdown()
    _cache.set(cache_key, {"result": md})
    return md


if __name__ == "__main__":
    mcp.run()
