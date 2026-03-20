"""Tests for Semantic Scholar MCP Server."""

import pytest
import respx
from httpx import Response

from semantic_scholar_mcp.client import BASE_URL
from semantic_scholar_mcp.server import _cache, _client, mcp, search_papers, get_citations, get_references, get_author

SAMPLE_PAPER = {
    "paperId": "abc123",
    "title": "Attention Is All You Need",
    "authors": [{"authorId": "1", "name": "Ashish Vaswani"}],
    "year": 2017,
    "abstract": "The dominant sequence transduction models...",
    "citationCount": 50000,
    "referenceCount": 40,
    "venue": "NeurIPS",
    "url": "https://www.semanticscholar.org/paper/abc123",
    "externalIds": {"DOI": "10.5555/3295222.3295349", "ArXiv": "1706.03762"},
    "fieldsOfStudy": ["Computer Science"],
}

SAMPLE_AUTHOR = {
    "authorId": "auth1",
    "name": "Ashish Vaswani",
    "paperCount": 50,
    "citationCount": 100000,
    "hIndex": 30,
}


@pytest.fixture(autouse=True)
def _disable_rate_limit():
    """Disable rate limiting for tests."""
    original = _client._min_interval
    _client._min_interval = 0.0
    yield
    _client._min_interval = original


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear cache between tests."""
    import shutil

    if _cache.cache_dir.exists():
        shutil.rmtree(_cache.cache_dir)
    _cache.cache_dir.mkdir(parents=True, exist_ok=True)
    yield


def test_server_name():
    assert mcp.name == "semantic-scholar-mcp"


def test_tools_registered():
    assert len(mcp._tool_manager._tools) >= 4


@respx.mock
@pytest.mark.asyncio
async def test_search_papers_returns_markdown():
    respx.get(f"{BASE_URL}/paper/search").mock(
        return_value=Response(200, json={"total": 1, "data": [SAMPLE_PAPER]})
    )
    result = await search_papers("attention")
    assert "Semantic Scholar Search" in result
    assert "Attention Is All You Need" in result
    assert "Ashish Vaswani" in result
    assert "NeurIPS" in result
    assert "50000" in result


@respx.mock
@pytest.mark.asyncio
async def test_search_papers_no_results():
    respx.get(f"{BASE_URL}/paper/search").mock(
        return_value=Response(200, json={"total": 0, "data": []})
    )
    result = await search_papers("nonexistent gibberish")
    assert "No results found" in result


@respx.mock
@pytest.mark.asyncio
async def test_search_papers_uses_cache():
    route = respx.get(f"{BASE_URL}/paper/search").mock(
        return_value=Response(200, json={"total": 1, "data": [SAMPLE_PAPER]})
    )
    result1 = await search_papers("attention", max_results=10)
    result2 = await search_papers("attention", max_results=10)
    assert result1 == result2
    assert route.call_count == 1  # Second call served from cache


@respx.mock
@pytest.mark.asyncio
async def test_get_citations_returns_markdown():
    respx.get(f"{BASE_URL}/paper/abc123/citations").mock(
        return_value=Response(
            200,
            json={"data": [{"citingPaper": SAMPLE_PAPER}]},
        )
    )
    result = await get_citations("abc123")
    assert "Citations for abc123" in result
    assert "Attention Is All You Need" in result


@respx.mock
@pytest.mark.asyncio
async def test_get_citations_no_results():
    respx.get(f"{BASE_URL}/paper/abc123/citations").mock(
        return_value=Response(200, json={"data": []})
    )
    result = await get_citations("abc123")
    assert "No citations found" in result


@respx.mock
@pytest.mark.asyncio
async def test_get_references_returns_markdown():
    respx.get(f"{BASE_URL}/paper/abc123/references").mock(
        return_value=Response(
            200,
            json={"data": [{"citedPaper": SAMPLE_PAPER}]},
        )
    )
    result = await get_references("abc123")
    assert "References for abc123" in result
    assert "Attention Is All You Need" in result


@respx.mock
@pytest.mark.asyncio
async def test_get_references_no_results():
    respx.get(f"{BASE_URL}/paper/abc123/references").mock(
        return_value=Response(200, json={"data": []})
    )
    result = await get_references("abc123")
    assert "No references found" in result


@respx.mock
@pytest.mark.asyncio
async def test_get_author_returns_markdown():
    respx.get(f"{BASE_URL}/author/auth1").mock(
        return_value=Response(200, json=SAMPLE_AUTHOR)
    )
    result = await get_author("auth1")
    assert "Ashish Vaswani" in result
    assert "h-index" in result
    assert "30" in result


@respx.mock
@pytest.mark.asyncio
async def test_get_author_not_found():
    respx.get(f"{BASE_URL}/author/unknown").mock(return_value=Response(404))
    result = await get_author("unknown")
    assert "No author found" in result


@respx.mock
@pytest.mark.asyncio
async def test_get_citations_uses_cache():
    route = respx.get(f"{BASE_URL}/paper/abc123/citations").mock(
        return_value=Response(
            200,
            json={"data": [{"citingPaper": SAMPLE_PAPER}]},
        )
    )
    result1 = await get_citations("abc123")
    result2 = await get_citations("abc123")
    assert result1 == result2
    assert route.call_count == 1
