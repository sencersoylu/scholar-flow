"""Tests for Document Export MCP Server."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import pytest_asyncio

from document_export_mcp.server import (
    build_submission_package,
    export_docx,
    export_latex,
    mcp,
    place_figures,
)

SAMPLE_MD = """\
# Test Paper

## Introduction

This is a **test** paper with *formatting*.

| Col A | Col B |
|-------|-------|
| 1     | 2     |
"""


def test_server_name():
    assert mcp.name == "document-export-mcp"


def test_tools_registered():
    # FastMCP stores tools internally - verify they exist
    assert len(mcp._tool_manager._tools) >= 4


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a mock project directory with typical files."""
    (tmp_path / "manuscript.md").write_text(SAMPLE_MD)
    (tmp_path / "references.bib").write_text("@article{smith2024, title={Test}}")
    (tmp_path / "cover_letter.md").write_text("Dear Editor,\n\nPlease consider.")
    fig_dir = tmp_path / "figures"
    fig_dir.mkdir()
    # Create a tiny valid PNG (1x1 pixel)
    _create_tiny_png(fig_dir / "fig1.png")
    return tmp_path


def _create_tiny_png(path: Path) -> None:
    """Create a minimal valid PNG file."""
    import struct
    import zlib

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw_data = b"\x00\xff\xff\xff"
    idat_data = zlib.compress(raw_data)

    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr_data)
    png += _chunk(b"IDAT", idat_data)
    png += _chunk(b"IEND", b"")
    path.write_bytes(png)


class TestExportDocx:
    @pytest.mark.asyncio
    async def test_export_success(self, tmp_path: Path):
        md_file = tmp_path / "test.md"
        md_file.write_text(SAMPLE_MD)
        output = tmp_path / "test.docx"
        result = await export_docx(str(md_file), output_path=str(output))
        assert "Export Successful" in result
        assert output.exists()

    @pytest.mark.asyncio
    async def test_export_default_output(self, tmp_path: Path):
        md_file = tmp_path / "test.md"
        md_file.write_text(SAMPLE_MD)
        result = await export_docx(str(md_file))
        assert "Export Successful" in result
        assert (tmp_path / "test.docx").exists()

    @pytest.mark.asyncio
    async def test_export_file_not_found(self, tmp_path: Path):
        result = await export_docx(str(tmp_path / "nonexistent.md"))
        assert "Error" in result


class TestExportLatex:
    @pytest.mark.asyncio
    async def test_export_success(self, tmp_path: Path):
        md_file = tmp_path / "test.md"
        md_file.write_text(SAMPLE_MD)
        output = tmp_path / "test.tex"
        result = await export_latex(str(md_file), output_path=str(output))
        assert "Export Successful" in result
        assert output.exists()

    @pytest.mark.asyncio
    async def test_export_default_output(self, tmp_path: Path):
        md_file = tmp_path / "test.md"
        md_file.write_text(SAMPLE_MD)
        result = await export_latex(str(md_file))
        assert "Export Successful" in result
        assert (tmp_path / "test.tex").exists()

    @pytest.mark.asyncio
    async def test_export_file_not_found(self, tmp_path: Path):
        result = await export_latex(str(tmp_path / "nonexistent.md"))
        assert "Error" in result


class TestPlaceFigures:
    @pytest.mark.asyncio
    async def test_place_in_markdown(self, project_dir: Path, tmp_path: Path):
        md_file = tmp_path / "ms.md"
        md_file.write_text("# Paper\n\n[FIGURE:fig1.png]\n\n## End\n")
        result = await place_figures(str(md_file), str(project_dir / "figures"))
        assert "Figures Placed" in result

    @pytest.mark.asyncio
    async def test_missing_manuscript(self, tmp_path: Path):
        result = await place_figures(
            str(tmp_path / "missing.md"), str(tmp_path / "figures")
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_missing_figures_dir(self, tmp_path: Path):
        md_file = tmp_path / "ms.md"
        md_file.write_text("# Paper\n")
        result = await place_figures(str(md_file), str(tmp_path / "no_figs"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_unsupported_format(self, tmp_path: Path):
        txt_file = tmp_path / "ms.txt"
        txt_file.write_text("hello")
        fig_dir = tmp_path / "figs"
        fig_dir.mkdir()
        result = await place_figures(str(txt_file), str(fig_dir))
        assert "Error" in result


class TestBuildSubmissionPackage:
    @pytest.mark.asyncio
    async def test_full_package(self, project_dir: Path, tmp_path: Path):
        output = tmp_path / "submission"
        result = await build_submission_package(str(project_dir), str(output))
        assert "Submission Package Report" in result
        assert "Manuscript" in result
        assert "Figures" in result
        assert "References" in result
        assert "Cover letter" in result

    @pytest.mark.asyncio
    async def test_missing_project(self, tmp_path: Path):
        result = await build_submission_package(
            str(tmp_path / "nonexistent"), str(tmp_path / "out")
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_partial_package(self, tmp_path: Path):
        project = tmp_path / "partial"
        project.mkdir()
        (project / "manuscript.md").write_text("# Paper\n")
        output = tmp_path / "submission"
        result = await build_submission_package(str(project), str(output))
        assert "Manuscript" in result
        assert "Missing" in result
        assert "Bibliography" in result  # should note missing bib
