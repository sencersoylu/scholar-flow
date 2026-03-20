"""Tests for Citation MCP Server."""

import json
import tempfile
from pathlib import Path

import httpx
import pytest
import respx

from citation_mcp.server import (
    mcp,
    resolve_doi,
    parse_bibtex_file,
    format_citation,
    check_references,
    _client,
)
from citation_mcp.client import BASE_URL


def test_server_name():
    assert mcp.name == "citation-mcp"


def test_tools_registered():
    assert len(mcp._tool_manager._tools) >= 4


SAMPLE_CROSSREF = {
    "status": "ok",
    "message": {
        "DOI": "10.1038/s41586-020-2649-2",
        "type": "journal-article",
        "title": ["AlphaFold paper"],
        "author": [{"given": "John", "family": "Jumper"}],
        "container-title": ["Nature"],
        "issued": {"date-parts": [[2021]]},
        "volume": "596",
        "issue": "7873",
        "page": "583-589",
    },
}


@respx.mock
async def test_resolve_doi_tool():
    respx.get(f"{BASE_URL}/works/10.1038/s41586-020-2649-2").mock(
        return_value=httpx.Response(200, json=SAMPLE_CROSSREF)
    )

    result = await resolve_doi("10.1038/s41586-020-2649-2")
    assert "AlphaFold paper" in result
    assert "Jumper, John" in result
    assert "Nature" in result
    assert "```bibtex" in result
    assert "@article{Jumper2021," in result


@respx.mock
async def test_resolve_doi_error():
    respx.get(f"{BASE_URL}/works/10.1234/bad").mock(
        return_value=httpx.Response(404)
    )

    result = await resolve_doi("10.1234/bad")
    assert "Error" in result


async def test_parse_bibtex_file_tool():
    bib_content = """@article{Smith2020,
  author  = {Smith, John and Doe, Jane},
  title   = {A Great Paper},
  journal = {Nature},
  year    = {2020},
  volume  = {123},
  pages   = {1--10},
  doi     = {10.1234/test},
}
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        f.write(bib_content)
        f.flush()
        result = await parse_bibtex_file(f.name)

    assert "Smith2020" in result
    assert "A Great Paper" in result
    assert "Smith, John" in result
    assert "1 entries" in result or "1**" in result


async def test_parse_bibtex_file_not_found():
    result = await parse_bibtex_file("/nonexistent/file.bib")
    assert "Error" in result
    assert "not found" in result


async def test_parse_bibtex_file_with_issues():
    # Missing required field (no author)
    bib_content = """@article{BadEntry,
  title   = {Missing Author},
  journal = {Some Journal},
  year    = {2020},
}
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
        f.write(bib_content)
        f.flush()
        result = await parse_bibtex_file(f.name)

    assert "Missing required field" in result
    assert "author" in result


async def test_format_citation_apa():
    ref_data = {
        "title": "A Great Paper",
        "authors": ["Smith, John", "Doe, Jane"],
        "year": "2020",
        "journal": "Nature",
        "volume": "123",
        "issue": "4",
        "pages": "1--10",
        "doi": "10.1234/test",
    }
    result = await format_citation(json.dumps(ref_data), "apa")
    assert "APA" in result
    assert "Smith, J." in result
    assert "Doe, J." in result
    assert "(2020)" in result
    assert "*Nature*" in result
    assert "https://doi.org/10.1234/test" in result


async def test_format_citation_ama():
    ref_data = {
        "title": "A Great Paper",
        "authors": ["Smith, John", "Doe, Jane"],
        "year": "2020",
        "journal": "Nature",
        "volume": "123",
        "issue": "4",
        "pages": "1--10",
        "doi": "10.1234/test",
    }
    result = await format_citation(json.dumps(ref_data), "ama")
    assert "AMA" in result
    assert "Smith J" in result
    assert "doi:10.1234/test" in result


async def test_format_citation_ieee():
    ref_data = {
        "title": "A Great Paper",
        "authors": ["Smith, John", "Doe, Jane"],
        "year": "2020",
        "journal": "Nature",
        "volume": "123",
        "pages": "1--10",
    }
    result = await format_citation(json.dumps(ref_data), "ieee")
    assert "IEEE" in result
    assert "J. Smith" in result
    assert "vol. 123" in result


async def test_format_citation_vancouver():
    ref_data = {
        "title": "A Great Paper",
        "authors": ["Smith, John"],
        "year": "2020",
        "journal": "Nature",
        "volume": "123",
    }
    result = await format_citation(json.dumps(ref_data), "vancouver")
    assert "Vancouver" in result.upper() or "VANCOUVER" in result


async def test_format_citation_unknown_style():
    ref_data = {"title": "Test", "authors": []}
    result = await format_citation(json.dumps(ref_data), "chicago")
    assert "Error" in result
    assert "Unknown style" in result


async def test_format_citation_bad_json():
    result = await format_citation("not valid json", "apa")
    assert "Error" in result


async def test_check_references_all_matched():
    bib_content = """@article{Smith2020,
  author  = {Smith, John},
  title   = {A Great Paper},
  journal = {Nature},
  year    = {2020},
  doi     = {10.1234/test},
}

@article{Doe2021,
  author  = {Doe, Jane},
  title   = {Another Paper},
  journal = {Science},
  year    = {2021},
  doi     = {10.1234/test2},
}
"""
    ms_content = r"""
\section{Introduction}
As shown by \cite{Smith2020}, the results are significant.
Further work by \citep{Doe2021} confirmed this.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as ms_f:
        ms_f.write(ms_content)
        ms_f.flush()
        ms_path = ms_f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as bib_f:
        bib_f.write(bib_content)
        bib_f.flush()
        bib_path = bib_f.name

    result = await check_references(ms_path, bib_path)
    assert "All clear" in result
    assert "Citations found in manuscript:** 2" in result


async def test_check_references_missing_and_unused():
    bib_content = """@article{Smith2020,
  author  = {Smith, John},
  title   = {A Paper},
  journal = {Nature},
  year    = {2020},
  doi     = {10.1234/test},
}

@article{Unused2019,
  author  = {Nobody, X},
  title   = {Unused Paper},
  journal = {Nowhere},
  year    = {2019},
  doi     = {10.1234/unused},
}
"""
    ms_content = r"""
\section{Introduction}
See \cite{Smith2020} and \cite{Missing2022}.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as ms_f:
        ms_f.write(ms_content)
        ms_f.flush()
        ms_path = ms_f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as bib_f:
        bib_f.write(bib_content)
        bib_f.flush()
        bib_path = bib_f.name

    result = await check_references(ms_path, bib_path)
    assert "Missing from bibliography" in result
    assert "`Missing2022`" in result
    assert "Unused bibliography entries" in result
    assert "`Unused2019`" in result


async def test_check_references_multiple_keys_in_cite():
    bib_content = """@article{A2020,
  author = {A, X}, title = {Paper A}, journal = {J}, year = {2020}, doi = {10/a},
}
@article{B2021,
  author = {B, Y}, title = {Paper B}, journal = {J}, year = {2021}, doi = {10/b},
}
"""
    ms_content = r"Results confirmed \cite{A2020,B2021}."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as ms_f:
        ms_f.write(ms_content)
        ms_f.flush()
        ms_path = ms_f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as bib_f:
        bib_f.write(bib_content)
        bib_f.flush()
        bib_path = bib_f.name

    result = await check_references(ms_path, bib_path)
    assert "All clear" in result


async def test_check_references_file_not_found():
    result = await check_references("/nonexistent/ms.tex", "/nonexistent/refs.bib")
    assert "Error" in result
