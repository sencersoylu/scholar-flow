"""Tests for arXiv MCP Server tools."""

import pytest
import httpx
import respx

from arxiv_mcp.server import mcp, search_arxiv, get_paper, get_latex_source
from fixtures import SAMPLE_ARXIV_RESPONSE, SAMPLE_ARXIV_SINGLE


def test_server_name():
    assert mcp.name == "arxiv-mcp"


def test_tools_registered():
    assert len(mcp._tool_manager._tools) >= 3


@pytest.mark.asyncio
@respx.mock
async def test_search_arxiv_tool():
    respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=SAMPLE_ARXIV_RESPONSE)
    )
    result = await search_arxiv("transformer attention", max_results=2)
    assert "Attention Is All You Need" in result
    assert "150" in result


@pytest.mark.asyncio
@respx.mock
async def test_search_arxiv_with_category():
    respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=SAMPLE_ARXIV_RESPONSE)
    )
    result = await search_arxiv("transformer", category="cs.CL", max_results=2)
    assert "Attention Is All You Need" in result


@pytest.mark.asyncio
@respx.mock
async def test_get_paper_tool():
    respx.get("http://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=SAMPLE_ARXIV_SINGLE)
    )
    result = await get_paper("2401.12345")
    assert "Attention Is All You Need" in result
    assert "John Smith" in result


@pytest.mark.asyncio
async def test_get_latex_source_tool():
    result = await get_latex_source("2401.12345")
    assert "https://arxiv.org/e-print/2401.12345" in result
