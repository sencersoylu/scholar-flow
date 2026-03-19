"""Tests for arXiv Atom XML parser."""

from arxiv_mcp.parser import parse_search_response, _parse_entry
from fixtures import SAMPLE_ARXIV_RESPONSE, SAMPLE_ARXIV_SINGLE


def test_parse_search_response():
    papers, total = parse_search_response(SAMPLE_ARXIV_RESPONSE)
    assert total == 150
    assert len(papers) == 1
    paper = papers[0]
    assert paper.arxiv_id == "2401.12345"
    assert paper.title == "Attention Is All You Need Revisited"
    assert paper.authors == ["John Smith", "Alice Doe"]
    assert "cs.CL" in paper.categories
    assert paper.doi == "10.1234/example"


def test_parse_paper_entry():
    papers, _ = parse_search_response(SAMPLE_ARXIV_SINGLE)
    assert len(papers) == 1
    assert papers[0].pdf_url == "http://arxiv.org/pdf/2401.12345v2"
