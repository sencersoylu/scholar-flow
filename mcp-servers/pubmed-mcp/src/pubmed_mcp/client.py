"""PubMed E-utilities API client."""

import asyncio
import os
from xml.etree import ElementTree

import httpx

from pubmed_mcp.models import Article

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class PubMedClient:
    def __init__(self, api_key: str | None = None, min_interval: float | None = None):
        self.api_key = api_key or os.environ.get("NCBI_API_KEY")
        if min_interval is not None:
            self._min_interval = min_interval
        else:
            self._min_interval = 0.1 if self.api_key else 0.34  # 10/sec or 3/sec
        self._last_request = 0.0

    async def _rate_limit(self):
        loop = asyncio.get_running_loop()
        now = loop.time()
        wait = self._min_interval - (now - self._last_request)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request = asyncio.get_running_loop().time()

    def _base_params(self) -> dict:
        params = {}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    async def search(self, query: str, max_results: int = 20) -> tuple[list[str], int]:
        """Search PubMed and return (list of PMIDs, total count)."""
        await self._rate_limit()
        params = {
            **self._base_params(),
            "db": "pubmed",
            "term": query,
            "retmax": str(max_results),
            "retmode": "xml",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/esearch.fcgi", params=params)
            resp.raise_for_status()

        root = ElementTree.fromstring(resp.text)
        count = int(root.findtext("Count", "0"))
        pmids = [id_el.text for id_el in root.findall(".//IdList/Id") if id_el.text]
        return pmids, count

    async def fetch_articles(self, pmids: list[str]) -> list[Article]:
        """Fetch article details by PMIDs."""
        if not pmids:
            return []
        await self._rate_limit()
        params = {
            **self._base_params(),
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/efetch.fcgi", params=params)
            resp.raise_for_status()

        return self._parse_articles(resp.text)

    def _parse_articles(self, xml_text: str) -> list[Article]:
        root = ElementTree.fromstring(xml_text)
        articles = []
        for pa in root.findall(".//PubmedArticle"):
            mc = pa.find("MedlineCitation")
            if mc is None:
                continue

            pmid = mc.findtext("PMID", "")
            article_el = mc.find("Article")
            if article_el is None:
                continue

            title = article_el.findtext("ArticleTitle", "")

            authors = []
            for author in article_el.findall(".//Author"):
                last = author.findtext("LastName", "")
                init = author.findtext("Initials", "")
                if last:
                    authors.append(f"{last} {init}".strip())

            journal = article_el.findtext(".//Journal/Title", "")

            year = (
                article_el.findtext(".//ArticleDate/Year", "")
                or mc.findtext(".//PubDate/Year", "")
                or ""
            )

            abstract_parts = []
            for at in article_el.findall(".//Abstract/AbstractText"):
                if at.text:
                    abstract_parts.append(at.text)
            abstract = " ".join(abstract_parts)

            doi = ""
            pd = pa.find("PubmedData")
            if pd is not None:
                for aid in pd.findall(".//ArticleId"):
                    if aid.get("IdType") == "doi" and aid.text:
                        doi = aid.text
                        break

            mesh_terms = []
            for mh in mc.findall(".//MeshHeading/DescriptorName"):
                if mh.text:
                    mesh_terms.append(mh.text)

            articles.append(Article(
                pmid=pmid,
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=abstract,
                doi=doi,
                mesh_terms=mesh_terms,
            ))
        return articles

    async def search_mesh_terms(self, term: str) -> str:
        """Search MeSH vocabulary and return translated terms."""
        await self._rate_limit()
        params = {
            **self._base_params(),
            "db": "mesh",
            "term": term,
            "retmode": "xml",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/esearch.fcgi", params=params)
            resp.raise_for_status()

        root = ElementTree.fromstring(resp.text)
        translations = []
        for tr in root.findall(".//Translation"):
            to_text = tr.findtext("To", "")
            if to_text:
                translations.append(to_text)
        return "; ".join(translations) if translations else f"No MeSH translation found for: {term}"
