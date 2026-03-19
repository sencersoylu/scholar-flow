"""arXiv API client."""

import asyncio

import httpx

from arxiv_mcp.models import Paper
from arxiv_mcp.parser import parse_search_response

BASE_URL = "http://export.arxiv.org/api/query"


class ArxivClient:
    def __init__(self, min_interval: float = 3.0):
        self._min_interval = min_interval  # arXiv rate limit: 1 req per 3 seconds
        self._last_request = 0.0

    async def _rate_limit(self):
        loop = asyncio.get_running_loop()
        now = loop.time()
        wait = self._min_interval - (now - self._last_request)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request = asyncio.get_running_loop().time()

    async def search(
        self, query: str, category: str = "", max_results: int = 20
    ) -> tuple[list[Paper], int]:
        """Search arXiv and return (papers, total_count)."""
        await self._rate_limit()

        search_query = query
        if category:
            search_query = f"cat:{category} AND all:{query}"

        params = {
            "search_query": search_query,
            "start": "0",
            "max_results": str(max_results),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()

        return parse_search_response(resp.text)

    async def get_paper(self, arxiv_id: str) -> Paper | None:
        """Get a single paper by arXiv ID."""
        await self._rate_limit()
        params = {"id_list": arxiv_id}
        async with httpx.AsyncClient() as client:
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()

        papers, _ = parse_search_response(resp.text)
        return papers[0] if papers else None

    async def get_latex_source_url(self, arxiv_id: str) -> str:
        """Return the URL for downloading LaTeX source."""
        return f"https://arxiv.org/e-print/{arxiv_id}"
