"""Tests for PubMed data models."""

from pubmed_mcp.models import Article, SearchResult


def test_article_creation():
    article = Article(
        pmid="12345678",
        title="Effect of X on Y",
        authors=["Smith J", "Doe A"],
        journal="JAMA",
        year="2024",
        abstract="Background: ... Methods: ... Results: ...",
        doi="10.1001/jama.2024.1234",
        mesh_terms=["Diabetes Mellitus", "Treatment Outcome"],
    )
    assert article.pmid == "12345678"
    assert len(article.authors) == 2
    assert article.doi == "10.1001/jama.2024.1234"


def test_article_to_markdown():
    article = Article(
        pmid="12345678",
        title="Effect of X on Y",
        authors=["Smith J", "Doe A"],
        journal="JAMA",
        year="2024",
        abstract="Background text here.",
        doi="10.1001/jama.2024.1234",
        mesh_terms=["Diabetes Mellitus"],
    )
    md = article.to_markdown()
    assert "Effect of X on Y" in md
    assert "Smith J" in md
    assert "JAMA" in md
    assert "12345678" in md


def test_search_result():
    result = SearchResult(
        query="diabetes treatment",
        total_count=1500,
        returned_count=20,
        articles=[],
    )
    assert result.total_count == 1500
    assert result.returned_count == 20
