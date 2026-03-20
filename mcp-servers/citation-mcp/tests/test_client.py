"""Tests for CrossRef API client."""

import pytest
import httpx
import respx

from citation_mcp.client import CrossRefClient, BASE_URL


SAMPLE_WORK_RESPONSE = {
    "status": "ok",
    "message": {
        "DOI": "10.1038/s41586-020-2649-2",
        "type": "journal-article",
        "title": ["Highly accurate protein structure prediction with AlphaFold"],
        "author": [
            {"given": "John", "family": "Jumper"},
            {"given": "Richard", "family": "Evans"},
        ],
        "container-title": ["Nature"],
        "issued": {"date-parts": [[2021]]},
        "volume": "596",
        "issue": "7873",
        "page": "583-589",
    },
}

SAMPLE_SEARCH_RESPONSE = {
    "status": "ok",
    "message": {
        "items": [
            {
                "DOI": "10.1038/s41586-020-2649-2",
                "type": "journal-article",
                "title": ["Highly accurate protein structure prediction with AlphaFold"],
                "author": [{"given": "John", "family": "Jumper"}],
                "container-title": ["Nature"],
                "issued": {"date-parts": [[2021]]},
                "volume": "596",
                "page": "583-589",
            },
            {
                "DOI": "10.1126/science.abc4346",
                "type": "journal-article",
                "title": ["Some other paper"],
                "author": [{"given": "Jane", "family": "Doe"}],
                "container-title": ["Science"],
                "issued": {"date-parts": [[2020]]},
            },
        ],
    },
}


@pytest.fixture
def client():
    return CrossRefClient(email="test@example.com", min_interval=0.0)


@respx.mock
async def test_resolve_doi(client):
    route = respx.get(f"{BASE_URL}/works/10.1038/s41586-020-2649-2").mock(
        return_value=httpx.Response(200, json=SAMPLE_WORK_RESPONSE)
    )

    ref = await client.resolve_doi("10.1038/s41586-020-2649-2")

    assert route.called
    assert ref.doi == "10.1038/s41586-020-2649-2"
    assert ref.title == "Highly accurate protein structure prediction with AlphaFold"
    assert len(ref.authors) == 2
    assert ref.authors[0] == "Jumper, John"
    assert ref.authors[1] == "Evans, Richard"
    assert ref.journal == "Nature"
    assert ref.year == "2021"
    assert ref.volume == "596"
    assert ref.issue == "7873"
    assert ref.pages == "583--589"
    assert ref.entry_type == "article"
    assert ref.bibtex_key == "Jumper2021"


@respx.mock
async def test_resolve_doi_not_found(client):
    respx.get(f"{BASE_URL}/works/10.1234/nonexistent").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await client.resolve_doi("10.1234/nonexistent")


@respx.mock
async def test_search_works(client):
    route = respx.get(f"{BASE_URL}/works").mock(
        return_value=httpx.Response(200, json=SAMPLE_SEARCH_RESPONSE)
    )

    refs = await client.search_works("AlphaFold", limit=5)

    assert route.called
    assert len(refs) == 2
    assert refs[0].doi == "10.1038/s41586-020-2649-2"
    assert refs[0].title == "Highly accurate protein structure prediction with AlphaFold"
    assert refs[1].doi == "10.1126/science.abc4346"
    assert refs[1].title == "Some other paper"


@respx.mock
async def test_search_works_empty(client):
    respx.get(f"{BASE_URL}/works").mock(
        return_value=httpx.Response(200, json={"status": "ok", "message": {"items": []}})
    )

    refs = await client.search_works("nonexistent query")
    assert refs == []


@respx.mock
async def test_resolve_doi_includes_mailto(client):
    route = respx.get(f"{BASE_URL}/works/10.1038/test").mock(
        return_value=httpx.Response(200, json={"status": "ok", "message": {
            "DOI": "10.1038/test", "title": ["Test"], "author": [],
            "container-title": [], "issued": {"date-parts": [[2021]]},
        }})
    )

    await client.resolve_doi("10.1038/test")
    assert route.called
    # Verify the mailto param was sent
    call = route.calls[0]
    assert "mailto" in str(call.request.url)
    assert "test@example.com" in str(call.request.url)


def test_make_bibtex_key():
    client = CrossRefClient(min_interval=0.0)
    assert client._make_bibtex_key(["Smith, John"], "2023") == "Smith2023"
    assert client._make_bibtex_key(["O'Brien, Jane"], "2020") == "OBrien2020"
    assert client._make_bibtex_key([], "2021") == "Unknown2021"


def test_parse_reference_book_type():
    client = CrossRefClient(min_interval=0.0)
    item = {
        "DOI": "10.1000/book",
        "type": "book",
        "title": ["A Great Book"],
        "author": [{"given": "Alice", "family": "Author"}],
        "container-title": [],
        "issued": {"date-parts": [[2019]]},
    }
    ref = client._parse_reference(item)
    assert ref.entry_type == "book"
    assert ref.bibtex_key == "Author2019"


def test_parse_reference_missing_fields():
    client = CrossRefClient(min_interval=0.0)
    item = {"DOI": "10.1000/minimal", "title": [], "issued": {}}
    ref = client._parse_reference(item)
    assert ref.doi == "10.1000/minimal"
    assert ref.title == ""
    assert ref.year == ""
    assert ref.authors == []
