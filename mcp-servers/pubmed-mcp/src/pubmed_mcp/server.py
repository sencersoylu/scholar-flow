"""PubMed MCP Server — NCBI E-utilities API integration."""

from mcp.server.fastmcp import FastMCP

from pubmed_mcp.client import PubMedClient
from pubmed_mcp.models import SearchResult

mcp = FastMCP("pubmed-mcp")

_client = PubMedClient()


@mcp.tool()
async def search_pubmed(query: str, max_results: int = 20) -> str:
    """Search PubMed for articles matching a query. Supports MeSH terms.

    Returns formatted markdown with article titles, authors, journals, abstracts, and MeSH terms.
    """
    pmids, total = await _client.search(query, max_results=max_results)
    if not pmids:
        return f"No results found for: {query}"

    articles = await _client.fetch_articles(pmids)
    result = SearchResult(
        query=query,
        total_count=total,
        returned_count=len(articles),
        articles=articles,
    )
    return result.to_markdown()


@mcp.tool()
async def get_article(pmid: str) -> str:
    """Get detailed article information by PubMed ID (PMID).

    Returns title, authors, journal, abstract, DOI, and MeSH terms.
    """
    articles = await _client.fetch_articles([pmid])
    if not articles:
        return f"No article found with PMID: {pmid}"
    return articles[0].to_markdown()


@mcp.tool()
async def search_mesh(term: str) -> str:
    """Search MeSH (Medical Subject Headings) vocabulary for standardized terms.

    Use this to find the correct MeSH terms before searching PubMed for more precise results.
    """
    return await _client.search_mesh_terms(term)


if __name__ == "__main__":
    mcp.run()
