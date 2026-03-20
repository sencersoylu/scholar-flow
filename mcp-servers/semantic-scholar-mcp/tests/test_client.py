"""Tests for Semantic Scholar API client with mocked HTTP responses."""

import pytest
import respx
from httpx import Response

from semantic_scholar_mcp.client import BASE_URL, SemanticScholarClient

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


@pytest.fixture
def client():
    return SemanticScholarClient(min_interval=0.0)


@respx.mock
@pytest.mark.asyncio
async def test_search_papers(client):
    respx.get(f"{BASE_URL}/paper/search").mock(
        return_value=Response(200, json={"total": 1, "data": [SAMPLE_PAPER]})
    )
    papers, total = await client.search_papers("attention")
    assert total == 1
    assert len(papers) == 1
    assert papers[0].paperId == "abc123"
    assert papers[0].title == "Attention Is All You Need"
    assert papers[0].year == 2017
    assert papers[0].citationCount == 50000


@respx.mock
@pytest.mark.asyncio
async def test_search_papers_empty(client):
    respx.get(f"{BASE_URL}/paper/search").mock(
        return_value=Response(200, json={"total": 0, "data": []})
    )
    papers, total = await client.search_papers("nonexistent gibberish query")
    assert total == 0
    assert papers == []


@respx.mock
@pytest.mark.asyncio
async def test_get_paper(client):
    respx.get(f"{BASE_URL}/paper/abc123").mock(
        return_value=Response(200, json=SAMPLE_PAPER)
    )
    paper = await client.get_paper("abc123")
    assert paper is not None
    assert paper.paperId == "abc123"
    assert paper.externalIds["DOI"] == "10.5555/3295222.3295349"


@respx.mock
@pytest.mark.asyncio
async def test_get_paper_not_found(client):
    respx.get(f"{BASE_URL}/paper/unknown").mock(return_value=Response(404))
    paper = await client.get_paper("unknown")
    assert paper is None


@respx.mock
@pytest.mark.asyncio
async def test_get_citations(client):
    respx.get(f"{BASE_URL}/paper/abc123/citations").mock(
        return_value=Response(
            200,
            json={"data": [{"citingPaper": SAMPLE_PAPER}]},
        )
    )
    papers = await client.get_citations("abc123")
    assert len(papers) == 1
    assert papers[0].title == "Attention Is All You Need"


@respx.mock
@pytest.mark.asyncio
async def test_get_citations_empty(client):
    respx.get(f"{BASE_URL}/paper/abc123/citations").mock(
        return_value=Response(200, json={"data": []})
    )
    papers = await client.get_citations("abc123")
    assert papers == []


@respx.mock
@pytest.mark.asyncio
async def test_get_references(client):
    respx.get(f"{BASE_URL}/paper/abc123/references").mock(
        return_value=Response(
            200,
            json={"data": [{"citedPaper": SAMPLE_PAPER}]},
        )
    )
    papers = await client.get_references("abc123")
    assert len(papers) == 1
    assert papers[0].title == "Attention Is All You Need"


@respx.mock
@pytest.mark.asyncio
async def test_get_references_skips_empty(client):
    respx.get(f"{BASE_URL}/paper/abc123/references").mock(
        return_value=Response(
            200,
            json={"data": [{"citedPaper": {"paperId": None}}]},
        )
    )
    papers = await client.get_references("abc123")
    assert papers == []


@respx.mock
@pytest.mark.asyncio
async def test_get_author(client):
    respx.get(f"{BASE_URL}/author/auth1").mock(
        return_value=Response(200, json=SAMPLE_AUTHOR)
    )
    author = await client.get_author("auth1")
    assert author is not None
    assert author.name == "Ashish Vaswani"
    assert author.hIndex == 30
    assert author.paperCount == 50


@respx.mock
@pytest.mark.asyncio
async def test_get_author_not_found(client):
    respx.get(f"{BASE_URL}/author/unknown").mock(return_value=Response(404))
    author = await client.get_author("unknown")
    assert author is None


@respx.mock
@pytest.mark.asyncio
async def test_api_key_header():
    client = SemanticScholarClient(api_key="test-key", min_interval=0.0)
    route = respx.get(f"{BASE_URL}/paper/search").mock(
        return_value=Response(200, json={"total": 0, "data": []})
    )
    await client.search_papers("test")
    assert route.calls[0].request.headers["x-api-key"] == "test-key"


@respx.mock
@pytest.mark.asyncio
async def test_no_api_key_no_header(client):
    route = respx.get(f"{BASE_URL}/paper/search").mock(
        return_value=Response(200, json={"total": 0, "data": []})
    )
    await client.search_papers("test")
    assert "x-api-key" not in route.calls[0].request.headers
