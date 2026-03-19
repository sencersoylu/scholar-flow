"""Tests for arXiv server caching behavior."""

import httpx
import pytest
import respx
from arxiv_mcp import server as server_module
from arxiv_mcp.cache import ResponseCache
from arxiv_mcp.server import search_arxiv
from fixtures import SAMPLE_ARXIV_RESPONSE


@pytest.fixture(autouse=True)
def fresh_cache(tmp_path, monkeypatch):
    test_cache = ResponseCache(cache_dir=tmp_path, ttl_seconds=3600)
    monkeypatch.setattr(server_module, "_cache", test_cache)
    return test_cache


@pytest.mark.asyncio
@respx.mock
async def test_search_uses_cache():
    route = respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=SAMPLE_ARXIV_RESPONSE)
    )

    result1 = await search_arxiv("transformer cache test", max_results=2)
    result2 = await search_arxiv("transformer cache test", max_results=2)

    assert result1 == result2
    assert route.call_count == 1
