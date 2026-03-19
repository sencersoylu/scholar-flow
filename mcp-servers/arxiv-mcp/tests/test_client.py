"""Tests for arXiv API client."""

import pytest
import httpx
import respx

from arxiv_mcp.client import ArxivClient
from fixtures import SAMPLE_ARXIV_RESPONSE, SAMPLE_ARXIV_SINGLE


@pytest.fixture
def client():
    return ArxivClient(min_interval=0)


@pytest.mark.asyncio
@respx.mock
async def test_search(client):
    respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=SAMPLE_ARXIV_RESPONSE)
    )
    papers, total = await client.search("transformer attention", max_results=2)
    assert total == 150
    assert len(papers) == 1
    assert papers[0].arxiv_id == "2401.12345"


@pytest.mark.asyncio
@respx.mock
async def test_search_with_category(client):
    respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=SAMPLE_ARXIV_RESPONSE)
    )
    papers, total = await client.search("transformer", category="cs.CL", max_results=2)
    assert total == 150


@pytest.mark.asyncio
@respx.mock
async def test_get_paper(client):
    respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=SAMPLE_ARXIV_SINGLE)
    )
    paper = await client.get_paper("2401.12345")
    assert paper is not None
    assert paper.title == "Attention Is All You Need Revisited"
    assert paper.authors == ["John Smith", "Alice Doe"]
