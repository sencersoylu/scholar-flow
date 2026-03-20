"""Semantic Scholar API client."""

from __future__ import annotations

import asyncio
import os

import httpx

from semantic_scholar_mcp.models import Author, Paper

BASE_URL = "https://api.semanticscholar.org/graph/v1"

PAPER_FIELDS = (
    "paperId,title,authors,year,abstract,citationCount,"
    "referenceCount,venue,url,externalIds,fieldsOfStudy"
)

AUTHOR_FIELDS = "authorId,name,paperCount,citationCount,hIndex"


class SemanticScholarClient:
    def __init__(self, api_key: str | None = None, min_interval: float | None = None):
        self.api_key = api_key or os.environ.get("S2_API_KEY")
        if min_interval is not None:
            self._min_interval = min_interval
        else:
            self._min_interval = 0.1 if self.api_key else 1.0  # 10/s or 1/s
        self._last_request = 0.0

    async def _rate_limit(self):
        loop = asyncio.get_running_loop()
        now = loop.time()
        wait = self._min_interval - (now - self._last_request)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request = asyncio.get_running_loop().time()

    def _headers(self) -> dict:
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def search_papers(
        self, query: str, limit: int = 20, fields: str = PAPER_FIELDS
    ) -> tuple[list[Paper], int]:
        """Search papers and return (list of Papers, total count)."""
        await self._rate_limit()
        params = {"query": query, "limit": str(limit), "fields": fields}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/paper/search",
                params=params,
                headers=self._headers(),
            )
            resp.raise_for_status()

        data = resp.json()
        total = data.get("total", 0)
        papers = [Paper(**self._clean_paper(p)) for p in data.get("data", [])]
        return papers, total

    async def get_paper(self, paper_id: str, fields: str = PAPER_FIELDS) -> Paper | None:
        """Get a single paper by ID (S2 paper ID, DOI, ArXiv ID, etc.)."""
        await self._rate_limit()
        params = {"fields": fields}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/paper/{paper_id}",
                params=params,
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()

        return Paper(**self._clean_paper(resp.json()))

    async def get_citations(
        self, paper_id: str, limit: int = 100, fields: str = PAPER_FIELDS
    ) -> list[Paper]:
        """Get papers that cite the given paper."""
        await self._rate_limit()
        params = {"fields": fields, "limit": str(limit)}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/paper/{paper_id}/citations",
                params=params,
                headers=self._headers(),
            )
            resp.raise_for_status()

        data = resp.json()
        papers = []
        for item in data.get("data", []):
            citing = item.get("citingPaper", {})
            if citing and citing.get("paperId"):
                papers.append(Paper(**self._clean_paper(citing)))
        return papers

    async def get_references(
        self, paper_id: str, limit: int = 100, fields: str = PAPER_FIELDS
    ) -> list[Paper]:
        """Get papers referenced by the given paper."""
        await self._rate_limit()
        params = {"fields": fields, "limit": str(limit)}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/paper/{paper_id}/references",
                params=params,
                headers=self._headers(),
            )
            resp.raise_for_status()

        data = resp.json()
        papers = []
        for item in data.get("data", []):
            cited = item.get("citedPaper", {})
            if cited and cited.get("paperId"):
                papers.append(Paper(**self._clean_paper(cited)))
        return papers

    async def get_author(self, author_id: str, fields: str = AUTHOR_FIELDS) -> Author | None:
        """Get author profile by ID."""
        await self._rate_limit()
        params = {"fields": fields}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/author/{author_id}",
                params=params,
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()

        data = resp.json()
        return Author(
            authorId=data.get("authorId", ""),
            name=data.get("name", ""),
            paperCount=data.get("paperCount", 0),
            citationCount=data.get("citationCount", 0),
            hIndex=data.get("hIndex", 0),
        )

    @staticmethod
    def _clean_paper(raw: dict) -> dict:
        """Normalize raw API response into Paper constructor kwargs."""
        return {
            "paperId": raw.get("paperId", ""),
            "title": raw.get("title", ""),
            "authors": raw.get("authors") or [],
            "year": raw.get("year"),
            "abstract": raw.get("abstract"),
            "citationCount": raw.get("citationCount", 0) or 0,
            "referenceCount": raw.get("referenceCount", 0) or 0,
            "venue": raw.get("venue", "") or "",
            "url": raw.get("url", "") or "",
            "externalIds": raw.get("externalIds") or {},
            "fieldsOfStudy": raw.get("fieldsOfStudy") or [],
        }
