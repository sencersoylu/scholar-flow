"""Tests for PubMed server caching behavior."""

import httpx
import pytest
import respx
from fixtures import SAMPLE_EFETCH_RESPONSE, SAMPLE_ESEARCH_RESPONSE
from pubmed_mcp import server as server_module
from pubmed_mcp.cache import ResponseCache
from pubmed_mcp.server import search_pubmed


@pytest.fixture(autouse=True)
def fresh_cache(tmp_path, monkeypatch):
    """Replace server cache with a fresh temp cache for each test."""
    test_cache = ResponseCache(cache_dir=tmp_path, ttl_seconds=3600)
    monkeypatch.setattr(server_module, "_cache", test_cache)
    return test_cache


@pytest.mark.asyncio
@respx.mock
async def test_search_uses_cache():
    """Second call with same query should not hit the API."""
    route = respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_ESEARCH_RESPONSE)
    )
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_EFETCH_RESPONSE)
    )

    # First call — hits API
    result1 = await search_pubmed("diabetes cache test", max_results=2)
    assert "Effect of Exercise" in result1

    # Second call with same query — should return cached result
    result2 = await search_pubmed("diabetes cache test", max_results=2)
    assert result1 == result2

    # esearch should only be called once (cached on second call)
    assert route.call_count == 1
