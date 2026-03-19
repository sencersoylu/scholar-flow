"""Tests for PubMed MCP Server tools."""

import httpx
import pytest
import respx
from fixtures import SAMPLE_EFETCH_RESPONSE, SAMPLE_ESEARCH_RESPONSE, SAMPLE_MESH_RESPONSE
from pubmed_mcp.server import get_article, mcp, search_mesh, search_pubmed


def test_server_name():
    assert mcp.name == "pubmed-mcp"


def test_tools_registered():
    assert len(mcp._tool_manager._tools) >= 3


@pytest.mark.asyncio
@respx.mock
async def test_search_pubmed_tool():
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_ESEARCH_RESPONSE)
    )
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_EFETCH_RESPONSE)
    )
    result = await search_pubmed("diabetes exercise", max_results=2)
    assert "Effect of Exercise" in result
    assert "1500" in result  # total count


@pytest.mark.asyncio
@respx.mock
async def test_get_article_tool():
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_EFETCH_RESPONSE)
    )
    result = await get_article("38000001")
    assert "Effect of Exercise" in result
    assert "Smith J" in result


@pytest.mark.asyncio
@respx.mock
async def test_search_mesh_tool():
    respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").mock(
        return_value=httpx.Response(200, text=SAMPLE_MESH_RESPONSE)
    )
    result = await search_mesh("diabetes")
    assert "Diabetes Mellitus" in result
