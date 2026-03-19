"""Tests for Semantic Scholar MCP Server."""

from semantic_scholar_mcp.server import mcp


def test_server_name():
    assert mcp.name == "semantic-scholar-mcp"


def test_tools_registered():
    # FastMCP stores tools internally - verify they exist
    assert len(mcp._tool_manager._tools) >= 4
