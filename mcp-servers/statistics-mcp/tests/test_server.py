"""Tests for Statistics MCP Server."""

from statistics_mcp.server import mcp


def test_server_name():
    assert mcp.name == "statistics-mcp"


def test_tools_registered():
    # FastMCP stores tools internally - verify they exist
    assert len(mcp._tool_manager._tools) >= 4
