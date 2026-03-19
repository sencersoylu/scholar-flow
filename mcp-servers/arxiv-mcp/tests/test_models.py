"""Tests for arXiv data models."""

from arxiv_mcp.models import Paper, SearchResult


def test_paper_creation():
    paper = Paper(
        arxiv_id="2401.12345",
        title="Attention Is All You Need Revisited",
        authors=["Smith J", "Doe A"],
        abstract="We revisit the transformer architecture...",
        categories=["cs.CL", "cs.AI"],
        published="2024-01-15",
        updated="2024-02-01",
        doi="10.1234/example",
        pdf_url="https://arxiv.org/pdf/2401.12345",
    )
    assert paper.arxiv_id == "2401.12345"
    assert "cs.CL" in paper.categories


def test_paper_to_markdown():
    paper = Paper(
        arxiv_id="2401.12345",
        title="Test Paper",
        authors=["Smith J"],
        abstract="Abstract text.",
        categories=["cs.CL"],
        published="2024-01-15",
        updated="2024-01-15",
        doi="",
        pdf_url="https://arxiv.org/pdf/2401.12345",
    )
    md = paper.to_markdown()
    assert "Test Paper" in md
    assert "2401.12345" in md
    assert "cs.CL" in md
