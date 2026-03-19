"""Tests for Journal Parser MCP Server."""

from journal_parser_mcp.server import mcp


def test_server_name():
    assert mcp.name == "journal-parser-mcp"


def test_tools_registered():
    # FastMCP stores tools internally - verify they exist
    assert len(mcp._tool_manager._tools) >= 3
