"""CrossRef API client."""

from __future__ import annotations

import asyncio
import os
import re

import httpx

from citation_mcp.models import Reference

BASE_URL = "https://api.crossref.org"


class CrossRefClient:
    def __init__(self, email: str | None = None, min_interval: float = 1.0):
        self.email = email or os.environ.get("CROSSREF_EMAIL")
        self._min_interval = min_interval
        self._last_request = 0.0

    async def _rate_limit(self) -> None:
        loop = asyncio.get_running_loop()
        now = loop.time()
        wait = self._min_interval - (now - self._last_request)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request = asyncio.get_running_loop().time()

    def _base_params(self) -> dict:
        params: dict[str, str] = {}
        if self.email:
            params["mailto"] = self.email
        return params

    def _parse_reference(self, item: dict) -> Reference:
        """Parse a CrossRef work item into a Reference."""
        # Authors
        authors: list[str] = []
        for a in item.get("author", []):
            given = a.get("given", "")
            family = a.get("family", "")
            if family and given:
                authors.append(f"{family}, {given}")
            elif family:
                authors.append(family)

        # Title
        titles = item.get("title", [])
        title = titles[0] if titles else ""

        # Year
        date_parts = item.get("issued", {}).get("date-parts", [[None]])
        year = str(date_parts[0][0]) if date_parts and date_parts[0] and date_parts[0][0] else ""

        # Journal
        containers = item.get("container-title", [])
        journal = containers[0] if containers else ""

        # Volume, issue, pages
        volume = item.get("volume", "")
        issue = item.get("issue", "")
        pages = item.get("page", "").replace("-", "--")

        # DOI
        doi = item.get("DOI", "")

        # Entry type
        entry_type = "article"
        cr_type = item.get("type", "")
        if "book" in cr_type:
            entry_type = "book"
        elif "proceedings" in cr_type or "conference" in cr_type:
            entry_type = "inproceedings"

        # BibTeX key
        bibtex_key = self._make_bibtex_key(authors, year)

        return Reference(
            doi=doi,
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            volume=volume,
            issue=issue,
            pages=pages,
            bibtex_key=bibtex_key,
            entry_type=entry_type,
        )

    @staticmethod
    def _make_bibtex_key(authors: list[str], year: str) -> str:
        """Generate a citation key like AuthorYYYY."""
        if authors:
            family = authors[0].split(",")[0].strip()
            family = re.sub(r"[^A-Za-z]", "", family)
        else:
            family = "Unknown"
        return f"{family}{year}"

    async def resolve_doi(self, doi: str) -> Reference:
        """Resolve a DOI via CrossRef and return a Reference."""
        await self._rate_limit()
        params = self._base_params()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/works/{doi}", params=params, timeout=30.0)
            resp.raise_for_status()
        data = resp.json()
        item = data.get("message", {})
        return self._parse_reference(item)

    async def search_works(self, query: str, limit: int = 5) -> list[Reference]:
        """Search CrossRef for works matching a query."""
        await self._rate_limit()
        params = {
            **self._base_params(),
            "query": query,
            "rows": str(limit),
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/works", params=params, timeout=30.0)
            resp.raise_for_status()
        data = resp.json()
        items = data.get("message", {}).get("items", [])
        return [self._parse_reference(item) for item in items]
