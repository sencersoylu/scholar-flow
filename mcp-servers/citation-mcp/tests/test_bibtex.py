"""Tests for BibTeX parsing, formatting, and validation."""

from citation_mcp.bibtex import format_bibtex, parse_bibtex, validate_bibtex
from citation_mcp.models import Reference


SAMPLE_BIB = """\
@article{Smith2020,
  author  = {Smith, John and Doe, Jane},
  title   = {A Great Paper on Testing},
  journal = {Journal of Testing},
  year    = {2020},
  volume  = {42},
  number  = {3},
  pages   = {100--110},
  doi     = {10.1234/test},
}

@inproceedings{Jones2019,
  author    = {Jones, Alice},
  title     = {Conference Talk},
  booktitle = {Proceedings of ICML},
  year      = {2019},
  doi       = {10.5678/conf},
}
"""


def test_parse_bibtex_basic():
    refs = parse_bibtex(SAMPLE_BIB)
    assert len(refs) == 2

    r1 = refs[0]
    assert r1.bibtex_key == "Smith2020"
    assert r1.entry_type == "article"
    assert r1.title == "A Great Paper on Testing"
    assert r1.authors == ["Smith, John", "Doe, Jane"]
    assert r1.journal == "Journal of Testing"
    assert r1.year == "2020"
    assert r1.volume == "42"
    assert r1.issue == "3"
    assert r1.pages == "100--110"
    assert r1.doi == "10.1234/test"

    r2 = refs[1]
    assert r2.bibtex_key == "Jones2019"
    assert r2.entry_type == "inproceedings"
    assert r2.journal == "Proceedings of ICML"  # booktitle mapped to journal


def test_parse_bibtex_empty():
    refs = parse_bibtex("")
    assert refs == []


def test_parse_bibtex_skips_non_entries():
    text = """\
@string{jrnl = {Journal of Testing}}
@comment{This is a comment}
@article{Real2020,
  author = {Real, Person},
  title  = {Actual Paper},
  journal = jrnl,
  year   = {2020},
  doi    = {10.1234/real},
}
"""
    refs = parse_bibtex(text)
    assert len(refs) == 1
    assert refs[0].bibtex_key == "Real2020"


def test_parse_bibtex_quoted_values():
    text = """\
@article{Test2021,
  author  = "Author, Test",
  title   = "A Quoted Title",
  journal = "Some Journal",
  year    = "2021",
  doi     = "10.1234/quoted",
}
"""
    refs = parse_bibtex(text)
    assert len(refs) == 1
    assert refs[0].title == "A Quoted Title"
    assert refs[0].authors == ["Author, Test"]


def test_format_bibtex_article():
    ref = Reference(
        doi="10.1234/test",
        title="A Great Paper",
        authors=["Smith, John", "Doe, Jane"],
        year="2020",
        journal="Nature",
        volume="42",
        issue="3",
        pages="1--10",
        bibtex_key="Smith2020",
        entry_type="article",
    )
    result = format_bibtex(ref)
    assert "@article{Smith2020," in result
    assert "author" in result
    assert "Smith, John and Doe, Jane" in result
    assert "{A Great Paper}" in result
    assert "journal" in result
    assert "Nature" in result
    assert "year" in result
    assert "2020" in result
    assert "doi" in result


def test_format_bibtex_book():
    ref = Reference(
        title="A Great Book",
        authors=["Author, A"],
        year="2019",
        journal="Publisher Press",
        bibtex_key="Author2019",
        entry_type="book",
    )
    result = format_bibtex(ref)
    assert "@book{Author2019," in result
    assert "booktitle" in result


def test_format_bibtex_minimal():
    ref = Reference(bibtex_key="Empty2020", entry_type="misc")
    result = format_bibtex(ref)
    assert "@misc{Empty2020," in result


def test_validate_bibtex_clean():
    bib = """\
@article{Clean2020,
  author  = {Author, A},
  title   = {Clean Paper},
  journal = {Clean Journal},
  year    = {2020},
  doi     = {10.1234/clean},
}
"""
    issues = validate_bibtex(bib)
    # No errors expected; may have warnings
    errors = [i for i in issues if i.severity == "error"]
    assert len(errors) == 0


def test_validate_bibtex_missing_fields():
    bib = """\
@article{Bad2020,
  title = {Only A Title},
}
"""
    issues = validate_bibtex(bib)
    errors = [i for i in issues if i.severity == "error"]
    error_messages = [e.message for e in errors]
    assert any("author" in m for m in error_messages)
    assert any("journal" in m for m in error_messages)
    assert any("year" in m for m in error_messages)


def test_validate_bibtex_duplicate_keys():
    bib = """\
@article{Dup2020,
  author = {A, B}, title = {First}, journal = {J}, year = {2020}, doi = {10/a},
}
@article{Dup2020,
  author = {C, D}, title = {Second}, journal = {J}, year = {2020}, doi = {10/b},
}
"""
    issues = validate_bibtex(bib)
    dup_issues = [i for i in issues if "Duplicate" in i.message]
    assert len(dup_issues) == 1


def test_validate_bibtex_bad_year():
    bib = """\
@article{BadYear,
  author  = {A, B},
  title   = {Paper},
  journal = {J},
  year    = {20twenty},
  doi     = {10/y},
}
"""
    issues = validate_bibtex(bib)
    year_issues = [i for i in issues if "Year" in i.message or "year" in i.message.lower()]
    assert len(year_issues) >= 1
    assert year_issues[0].severity == "warning"


def test_validate_bibtex_missing_doi():
    bib = """\
@article{NoDoi2020,
  author  = {A, B},
  title   = {Paper Without DOI},
  journal = {J},
  year    = {2020},
}
"""
    issues = validate_bibtex(bib)
    doi_issues = [i for i in issues if "DOI" in i.message or "doi" in i.message.lower()]
    assert len(doi_issues) >= 1
    assert doi_issues[0].severity == "warning"


def test_roundtrip_parse_format():
    """Parse BibTeX, format it back, and parse again -- data should match."""
    refs = parse_bibtex(SAMPLE_BIB)
    formatted = "\n\n".join(format_bibtex(r) for r in refs)
    refs2 = parse_bibtex(formatted)
    assert len(refs2) == len(refs)
    for r1, r2 in zip(refs, refs2):
        assert r1.bibtex_key == r2.bibtex_key
        assert r1.title == r2.title
        assert r1.year == r2.year
        assert r1.doi == r2.doi
