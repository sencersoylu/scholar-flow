"""Tests for PubMed E-utilities API client."""

import httpx
import pytest
import respx
from fixtures import SAMPLE_EFETCH_RESPONSE, SAMPLE_ESEARCH_RESPONSE, SAMPLE_MESH_RESPONSE
from pubmed_mcp.client import PubMedClient


@pytest.fixture
def client():
    return PubMedClient(api_key=None, min_interval=0)


@pytest.mark.asyncio
@respx.mock
async def test_search_returns_pmids(client):
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_ESEARCH_RESPONSE)
    )
    pmids, total = await client.search("diabetes exercise", max_results=2)
    assert pmids == ["38000001", "38000002"]
    assert total == 1500


@pytest.mark.asyncio
@respx.mock
async def test_fetch_articles(client):
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_EFETCH_RESPONSE)
    )
    articles = await client.fetch_articles(["38000001"])
    assert len(articles) == 1
    assert articles[0].pmid == "38000001"
    assert articles[0].title == "Effect of Exercise on Type 2 Diabetes"
    assert articles[0].authors == ["Smith J", "Doe A"]
    assert articles[0].journal == "JAMA"
    assert articles[0].doi == "10.1001/jama.2024.1234"
    assert "Diabetes Mellitus, Type 2" in articles[0].mesh_terms


@pytest.mark.asyncio
@respx.mock
async def test_search_mesh(client):
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_MESH_RESPONSE)
    )
    result = await client.search_mesh_terms("diabetes")
    assert "Diabetes Mellitus" in result


@pytest.mark.asyncio
@respx.mock
async def test_multiple_searches_succeed(client):
    route = respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_ESEARCH_RESPONSE)
    )
    # Multiple calls should all succeed
    for _ in range(3):
        await client.search("test", max_results=1)
    assert route.call_count == 3
