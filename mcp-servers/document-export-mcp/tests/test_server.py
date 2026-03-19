"""Tests for Document Export MCP Server."""

from document_export_mcp.server import mcp


def test_server_name():
    assert mcp.name == "document-export-mcp"


def test_tools_registered():
    # FastMCP stores tools internally - verify they exist
    assert len(mcp._tool_manager._tools) >= 4
