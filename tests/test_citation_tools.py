"""Comprehensive tests for the citation tool scripts.

Covers:
- doi_to_bibtex.py — CrossRef API interaction and BibTeX formatting
- pubmed_metadata.py — PubMed XML parsing and output formatting
- citation_validator.py — BibTeX validation and error detection
"""

from __future__ import annotations

import json
import sys
import textwrap
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Adjust sys.path so we can import the scripts as modules
# ---------------------------------------------------------------------------
sys.path.insert(
    0,
    str(
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "skills"
        / "publication"
        / "citation-tools"
        / "scripts"
    ),
)

import citation_validator as cv
import doi_to_bibtex as dtb
import pubmed_metadata as pm

# ===================================================================
# Fixtures & sample data
# ===================================================================

SAMPLE_CROSSREF_MESSAGE = {
    "message": {
        "type": "journal-article",
        "DOI": "10.1038/s41586-020-2649-2",
        "title": ["Highly accurate protein structure prediction with AlphaFold"],
        "author": [
            {"given": "John", "family": "Jumper"},
            {"given": "Richard", "family": "Evans"},
        ],
        "container-title": ["Nature"],
        "issued": {"date-parts": [[2021, 7]]},
        "volume": "596",
        "issue": "7873",
        "page": "583-589",
        "publisher": "Springer Science and Business Media LLC",
        "ISSN": ["0028-0836"],
        "URL": "http://dx.doi.org/10.1038/s41586-020-2649-2",
    }
}

SAMPLE_PUBMED_XML = textwrap.dedent("""\
    <?xml version="1.0" ?>
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <PMID>32284588</PMID>
          <Article>
            <ArticleTitle>Deep learning for computational biology.</ArticleTitle>
            <AuthorList>
              <Author>
                <LastName>Smith</LastName>
                <ForeName>John A</ForeName>
              </Author>
              <Author>
                <LastName>Doe</LastName>
                <ForeName>Jane</ForeName>
              </Author>
            </AuthorList>
            <Journal>
              <Title>Molecular Systems Biology</Title>
              <ISOAbbreviation>Mol Syst Biol</ISOAbbreviation>
              <JournalIssue>
                <Volume>16</Volume>
                <Issue>4</Issue>
                <PubDate>
                  <Year>2020</Year>
                  <Month>Apr</Month>
                </PubDate>
              </JournalIssue>
            </Journal>
            <Pagination>
              <MedlinePgn>e9198</MedlinePgn>
            </Pagination>
            <Abstract>
              <AbstractText>This is a sample abstract about deep learning.</AbstractText>
            </Abstract>
          </Article>
        </MedlineCitation>
        <PubmedData>
          <ArticleIdList>
            <ArticleId IdType="doi">10.15252/msb.20199198</ArticleId>
            <ArticleId IdType="pmc">PMC7170863</ArticleId>
          </ArticleIdList>
        </PubmedData>
      </PubmedArticle>
    </PubmedArticleSet>
""")

VALID_BIB = textwrap.dedent("""\
    @article{Smith2020,
      author  = {Smith, John A and Doe, Jane},
      title   = {Deep learning for computational biology},
      journal = {Molecular Systems Biology},
      year    = {2020},
      volume  = {16},
      pages   = {e9198},
      doi     = {10.15252/msb.20199198},
    }
""")


def _make_urlopen_response(data: bytes):
    """Create a mock context-manager response for urllib.request.urlopen."""
    resp = MagicMock()
    resp.read.return_value = data
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


# ===================================================================
# doi_to_bibtex tests
# ===================================================================


class TestDoiBibtexFormatting:
    """Tests for BibTeX formatting from CrossRef metadata."""

    def test_format_bibtex_basic(self):
        """Format a realistic CrossRef message into a valid BibTeX entry."""
        meta = SAMPLE_CROSSREF_MESSAGE["message"]
        result = dtb._format_bibtex(meta)

        assert result.startswith("@article{Jumper2021,")
        assert "Jumper, John" in result
        assert "Evans, Richard" in result
        assert "Nature" in result
        assert "2021" in result
        assert "583--589" in result
        assert "10.1038/s41586-020-2649-2" in result

    def test_make_cite_key_standard(self):
        """Citation key uses first author family name + year."""
        meta = {"author": [{"family": "Einstein"}], "issued": {"date-parts": [[1905]]}}
        assert dtb._make_cite_key(meta) == "Einstein1905"

    def test_make_cite_key_no_author(self):
        """Citation key falls back to 'Unknown' when no authors."""
        meta = {"issued": {"date-parts": [[2023]]}}
        assert dtb._make_cite_key(meta) == "Unknown2023"

    def test_make_cite_key_no_year_empty_date_parts(self):
        """Citation key uses XXXX when date-parts list is empty."""
        meta = {"author": [{"family": "Turing"}], "issued": {"date-parts": []}}
        assert dtb._make_cite_key(meta) == "TuringXXXX"

    def test_make_cite_key_no_issued_key(self):
        """Citation key handles completely missing 'issued' dict."""
        meta = {"author": [{"family": "Turing"}]}
        # When 'issued' is missing entirely, date_parts logic yields None
        result = dtb._make_cite_key(meta)
        assert result.startswith("Turing")

    def test_join_authors_multiple(self):
        """Multiple authors are joined with ' and '."""
        authors = [
            {"given": "Alice", "family": "Wang"},
            {"given": "Bob", "family": "Chen"},
        ]
        assert dtb._join_authors(authors) == "Wang, Alice and Chen, Bob"

    def test_join_authors_family_only(self):
        """Author with only family name is handled."""
        authors = [{"family": "Consortium"}]
        assert dtb._join_authors(authors) == "Consortium"

    def test_get_pages_normalises_dash(self):
        """Single hyphens in pages are normalised to double dashes."""
        meta = {"page": "100-200"}
        assert dtb._get_pages(meta) == "100--200"

    def test_format_bibtex_book_type(self):
        """Book type is detected from CrossRef type field."""
        meta = {
            "type": "book",
            "title": ["A Great Book"],
            "author": [{"given": "A", "family": "Author"}],
            "issued": {"date-parts": [[2022]]},
            "publisher": "Academic Press",
        }
        result = dtb._format_bibtex(meta)
        assert result.startswith("@book{")

    def test_format_bibtex_proceedings_type(self):
        """Proceedings type is detected from CrossRef type field."""
        meta = {
            "type": "proceedings-article",
            "title": ["A Conference Paper"],
            "author": [{"given": "B", "family": "Builder"}],
            "container-title": ["Proc. of Conf"],
            "issued": {"date-parts": [[2023]]},
        }
        result = dtb._format_bibtex(meta)
        assert result.startswith("@inproceedings{")
        assert "booktitle" in result

    def test_format_bibtex_missing_fields(self):
        """An empty metadata dict produces a minimal entry without crashing."""
        result = dtb._format_bibtex({})
        assert result.startswith("@article{Unknown")


class TestDoiFetch:
    """Tests for CrossRef API interaction (mocked)."""

    @patch("doi_to_bibtex.urllib.request.urlopen")
    def test_fetch_crossref_success(self, mock_urlopen):
        """Successful CrossRef fetch returns the message dict."""
        payload = json.dumps(SAMPLE_CROSSREF_MESSAGE).encode()
        mock_urlopen.return_value = _make_urlopen_response(payload)

        result = dtb._fetch_crossref("10.1038/s41586-020-2649-2")
        assert result["DOI"] == "10.1038/s41586-020-2649-2"

    @patch("doi_to_bibtex.urllib.request.urlopen")
    def test_fetch_crossref_404(self, mock_urlopen):
        """HTTP 404 raises ValueError with descriptive message."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=404, msg="Not Found", hdrs=None, fp=None  # type: ignore[arg-type]
        )
        with pytest.raises(ValueError, match="DOI not found"):
            dtb._fetch_crossref("10.9999/nonexistent")

    @patch("doi_to_bibtex.urllib.request.urlopen")
    def test_fetch_crossref_server_error(self, mock_urlopen):
        """HTTP 500 raises RuntimeError."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=500, msg="Server Error", hdrs=None, fp=None  # type: ignore[arg-type]
        )
        with pytest.raises(RuntimeError, match="HTTP 500"):
            dtb._fetch_crossref("10.1038/s41586-020-2649-2")

    @patch("doi_to_bibtex.urllib.request.urlopen")
    def test_fetch_crossref_network_error(self, mock_urlopen):
        """Network failure raises RuntimeError."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Name resolution failed")
        with pytest.raises(RuntimeError, match="Network error"):
            dtb._fetch_crossref("10.1038/s41586-020-2649-2")


class TestDoiCli:
    """Tests for doi_to_bibtex CLI argument parsing and main()."""

    def test_build_parser_required_doi(self):
        """Parser requires --doi argument."""
        parser = dtb._build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_build_parser_accepts_multiple_dois(self):
        """Parser accepts multiple DOIs."""
        parser = dtb._build_parser()
        args = parser.parse_args(["--doi", "10.1/a", "10.2/b"])
        assert args.doi == ["10.1/a", "10.2/b"]

    def test_build_parser_output_flag(self):
        """Parser accepts -o / --output flag."""
        parser = dtb._build_parser()
        args = parser.parse_args(["--doi", "10.1/a", "-o", "out.bib"])
        assert args.output == "out.bib"

    @patch("doi_to_bibtex.doi_to_bibtex")
    def test_main_stdout(self, mock_doi_to_bibtex, capsys):
        """main() writes BibTeX to stdout when no --output given."""
        mock_doi_to_bibtex.return_value = "@article{Test2024, title={Test}}"
        rc = dtb.main(["--doi", "10.1/test"])
        assert rc == 0
        assert "@article{Test2024" in capsys.readouterr().out

    @patch("doi_to_bibtex.doi_to_bibtex")
    def test_main_error_returns_nonzero(self, mock_doi_to_bibtex):
        """main() returns non-zero when all DOIs fail."""
        mock_doi_to_bibtex.side_effect = ValueError("DOI not found")
        rc = dtb.main(["--doi", "10.1/bad"])
        assert rc != 0


# ===================================================================
# pubmed_metadata tests
# ===================================================================


class TestPubmedParsing:
    """Tests for PubMed XML parsing."""

    def _parse_single(self) -> pm.ArticleMeta:
        """Helper: parse the sample XML and return the first article."""
        import xml.etree.ElementTree as ET

        root = ET.fromstring(SAMPLE_PUBMED_XML)
        articles = [pm._parse_article(pa) for pa in root.findall("PubmedArticle")]
        assert len(articles) == 1
        return articles[0]

    def test_parse_pmid(self):
        """PMID is correctly extracted."""
        meta = self._parse_single()
        assert meta.pmid == "32284588"

    def test_parse_title(self):
        """Article title is correctly extracted."""
        meta = self._parse_single()
        assert "Deep learning" in meta.title

    def test_parse_authors(self):
        """Authors list is correctly parsed."""
        meta = self._parse_single()
        assert meta.authors == ["Smith, John A", "Doe, Jane"]

    def test_parse_journal(self):
        """Journal name and abbreviation are parsed."""
        meta = self._parse_single()
        assert meta.journal == "Molecular Systems Biology"
        assert meta.journal_abbrev == "Mol Syst Biol"

    def test_parse_date(self):
        """Year and month are extracted from PubDate."""
        meta = self._parse_single()
        assert meta.year == "2020"
        assert meta.month == "Apr"

    def test_parse_volume_issue_pages(self):
        """Volume, issue, and pages are parsed."""
        meta = self._parse_single()
        assert meta.volume == "16"
        assert meta.issue == "4"
        assert meta.pages == "e9198"

    def test_parse_doi_and_pmc(self):
        """DOI and PMC identifiers are extracted from ArticleIdList."""
        meta = self._parse_single()
        assert meta.doi == "10.15252/msb.20199198"
        assert meta.pmc == "PMC7170863"

    def test_parse_abstract(self):
        """Abstract text is captured."""
        meta = self._parse_single()
        assert "deep learning" in meta.abstract.lower()


class TestPubmedFetch:
    """Tests for PubMed API interaction (mocked)."""

    @patch("pubmed_metadata.urllib.request.urlopen")
    def test_fetch_pubmed_success(self, mock_urlopen):
        """Successful PubMed fetch returns parsed articles."""
        mock_urlopen.return_value = _make_urlopen_response(SAMPLE_PUBMED_XML.encode())
        articles = pm.fetch_pubmed(["32284588"])
        assert len(articles) == 1
        assert articles[0].pmid == "32284588"

    @patch("pubmed_metadata.urllib.request.urlopen")
    def test_fetch_pubmed_network_error(self, mock_urlopen):
        """Network failure raises RuntimeError."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        with pytest.raises(RuntimeError, match="Failed to reach PubMed"):
            pm.fetch_pubmed(["99999999"])

    def test_fetch_pubmed_empty_input(self):
        """Empty PMID list returns empty result without making a request."""
        assert pm.fetch_pubmed([]) == []
        assert pm.fetch_pubmed(["", "  "]) == []

    @patch("pubmed_metadata.urllib.request.urlopen")
    def test_fetch_pubmed_no_articles_in_xml(self, mock_urlopen):
        """XML response with no PubmedArticle elements returns empty list."""
        xml = b'<?xml version="1.0" ?><PubmedArticleSet></PubmedArticleSet>'
        mock_urlopen.return_value = _make_urlopen_response(xml)
        articles = pm.fetch_pubmed(["00000000"])
        assert articles == []


class TestPubmedFormatters:
    """Tests for output formatting functions."""

    @pytest.fixture()
    def sample_meta(self) -> pm.ArticleMeta:
        return pm.ArticleMeta(
            pmid="32284588",
            title="Deep learning for computational biology",
            authors=["Smith, John A", "Doe, Jane"],
            journal="Molecular Systems Biology",
            journal_abbrev="Mol Syst Biol",
            year="2020",
            month="Apr",
            volume="16",
            issue="4",
            pages="e9198",
            doi="10.15252/msb.20199198",
            pmc="PMC7170863",
            abstract="Sample abstract.",
        )

    def test_to_bibtex_format(self, sample_meta):
        """BibTeX output contains expected fields."""
        bib = pm._to_bibtex(sample_meta)
        assert bib.startswith("@article{Smith2020,")
        assert "Smith, John A and Doe, Jane" in bib
        assert "journal" in bib
        assert "2020" in bib
        assert "doi" in bib

    def test_to_json_format(self, sample_meta):
        """JSON output is valid and contains expected data."""
        out = pm._to_json([sample_meta])
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["pmid"] == "32284588"
        assert data[0]["authors"] == ["Smith, John A", "Doe, Jane"]

    def test_to_text_format(self, sample_meta):
        """Text output contains human-readable fields."""
        txt = pm._to_text(sample_meta)
        assert "PMID:    32284588" in txt
        assert "Smith, John A; Doe, Jane" in txt
        assert "https://doi.org/10.15252/msb.20199198" in txt

    def test_to_bibtex_no_author(self):
        """BibTeX handles missing authors gracefully."""
        meta = pm.ArticleMeta(title="Orphan Paper", year="2023")
        bib = pm._to_bibtex(meta)
        assert "@article{Unknown2023," in bib
        assert "author" not in bib.split("\n", 1)[1]  # no author field line


class TestPubmedCli:
    """Tests for pubmed_metadata CLI."""

    def test_parser_requires_pmid(self):
        """Parser requires --pmid argument."""
        parser = pm._build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parser_format_choices(self):
        """Parser accepts bibtex, json, text formats."""
        parser = pm._build_parser()
        for fmt in ("bibtex", "json", "text"):
            args = parser.parse_args(["--pmid", "123", "--format", fmt])
            assert args.format == fmt

    @patch("pubmed_metadata.fetch_pubmed")
    def test_main_bibtex_stdout(self, mock_fetch, capsys):
        """main() outputs BibTeX to stdout."""
        mock_fetch.return_value = [
            pm.ArticleMeta(
                pmid="123",
                title="Test",
                authors=["Auth, A"],
                journal="J",
                year="2024",
            )
        ]
        rc = pm.main(["--pmid", "123"])
        assert rc == 0
        assert "@article{Auth2024," in capsys.readouterr().out

    @patch("pubmed_metadata.fetch_pubmed")
    def test_main_no_articles_returns_error(self, mock_fetch):
        """main() returns 1 when no articles found."""
        mock_fetch.return_value = []
        rc = pm.main(["--pmid", "99999"])
        assert rc == 1


# ===================================================================
# citation_validator tests
# ===================================================================


class TestBibParser:
    """Tests for the BibTeX parser."""

    def test_parse_valid_entry(self):
        """A well-formed entry is parsed correctly."""
        entries = cv.parse_bib(VALID_BIB)
        assert len(entries) == 1
        e = entries[0]
        assert e.entry_type == "article"
        assert e.cite_key == "Smith2020"
        assert e.fields["author"] == "Smith, John A and Doe, Jane"
        assert e.fields["year"] == "2020"

    def test_parse_multiple_entries(self):
        """Multiple entries in a single string are all parsed."""
        bib = VALID_BIB + "\n" + VALID_BIB.replace("Smith2020", "Jones2021")
        entries = cv.parse_bib(bib)
        assert len(entries) == 2

    def test_parse_skips_comments_and_strings(self):
        """@comment and @string blocks are not treated as entries."""
        bib = '@comment{This is ignored}\n@string{jnl = "My Journal"}\n' + VALID_BIB
        entries = cv.parse_bib(bib)
        assert len(entries) == 1

    def test_parse_empty_string(self):
        """Empty input returns no entries."""
        assert cv.parse_bib("") == []

    def test_parse_field_with_nested_braces(self):
        """Fields with nested braces (e.g. title with {LaTeX}) are handled."""
        bib = textwrap.dedent("""\
            @article{Test2020,
              author = {Author, A},
              title  = {{A} study of {DNA} methylation},
              journal = {Nature},
              year   = {2020},
              doi    = {10.1000/test},
            }
        """)
        entries = cv.parse_bib(bib)
        assert len(entries) == 1
        assert "DNA" in entries[0].fields["title"]


class TestValidation:
    """Tests for the validate() function."""

    def test_valid_entry_no_errors(self):
        """A complete valid entry produces no errors."""
        entries = cv.parse_bib(VALID_BIB)
        issues = cv.validate(entries)
        errors = [i for i in issues if i.severity is cv.Severity.ERROR]
        assert len(errors) == 0

    def test_missing_required_field(self):
        """Missing a required field (author) triggers an error."""
        bib = textwrap.dedent("""\
            @article{NoAuthor2020,
              title   = {A paper without an author},
              journal = {Some Journal},
              year    = {2020},
              doi     = {10.1000/test},
            }
        """)
        entries = cv.parse_bib(bib)
        issues = cv.validate(entries)
        errors = [i for i in issues if i.severity is cv.Severity.ERROR]
        assert any("author" in e.message for e in errors)

    def test_duplicate_citation_keys(self):
        """Duplicate citation keys are flagged as errors."""
        bib = VALID_BIB + "\n" + VALID_BIB  # same key twice
        entries = cv.parse_bib(bib)
        issues = cv.validate(entries)
        errors = [i for i in issues if i.severity is cv.Severity.ERROR]
        assert any("Duplicate" in e.message for e in errors)

    def test_missing_doi_warning(self):
        """Entry without DOI triggers a warning."""
        bib = textwrap.dedent("""\
            @article{NoDoi2020,
              author  = {Author, A},
              title   = {No DOI paper},
              journal = {Some Journal},
              year    = {2020},
            }
        """)
        entries = cv.parse_bib(bib)
        issues = cv.validate(entries)
        warnings = [i for i in issues if i.severity is cv.Severity.WARNING]
        assert any("DOI" in w.message for w in warnings)

    @pytest.mark.parametrize(
        "year_val,should_warn",
        [
            ("2020", False),
            ("20", True),
            ("forthcoming", True),
            ("2020a", True),
            ("99", True),
        ],
    )
    def test_year_format_validation(self, year_val, should_warn):
        """Year field is validated to be exactly 4 digits."""
        bib = textwrap.dedent(f"""\
            @article{{YearTest,
              author  = {{Author, A}},
              title   = {{Test}},
              journal = {{J}},
              year    = {{{year_val}}},
              doi     = {{10.1000/test}},
            }}
        """)
        entries = cv.parse_bib(bib)
        issues = cv.validate(entries)
        year_warnings = [
            i
            for i in issues
            if i.severity is cv.Severity.WARNING and "Year" in i.message
        ]
        if should_warn:
            assert len(year_warnings) > 0, f"Expected warning for year='{year_val}'"
        else:
            assert len(year_warnings) == 0, f"Unexpected warning for year='{year_val}'"

    def test_empty_field_warning(self):
        """An explicitly empty field triggers a warning."""
        bib = textwrap.dedent("""\
            @article{Empty2020,
              author  = {Author, A},
              title   = {Test},
              journal = {J},
              year    = {2020},
              doi     = {10.1000/test},
              volume  = {},
            }
        """)
        entries = cv.parse_bib(bib)
        issues = cv.validate(entries)
        warnings = [i for i in issues if i.severity is cv.Severity.WARNING]
        assert any("empty" in w.message.lower() for w in warnings)

    def test_book_requires_publisher(self):
        """A @book entry missing 'publisher' triggers an error."""
        bib = textwrap.dedent("""\
            @book{BookNoPub2020,
              author = {Writer, W},
              title  = {My Book},
              year   = {2020},
              doi    = {10.1000/book},
            }
        """)
        entries = cv.parse_bib(bib)
        issues = cv.validate(entries)
        errors = [i for i in issues if i.severity is cv.Severity.ERROR]
        assert any("publisher" in e.message for e in errors)


class TestValidatorStrictMode:
    """Tests for --strict flag behaviour in the CLI."""

    def test_strict_mode_fails_on_warnings(self, tmp_path):
        """With --strict, warnings cause non-zero exit code."""
        bib_file = tmp_path / "refs.bib"
        # Valid entry but missing DOI -> warning
        bib_file.write_text(textwrap.dedent("""\
            @article{Test2020,
              author  = {Author, A},
              title   = {Test},
              journal = {J},
              year    = {2020},
            }
        """))
        rc = cv.main(["--input", str(bib_file), "--strict"])
        assert rc == 1

    def test_non_strict_mode_passes_on_warnings(self, tmp_path):
        """Without --strict, warnings alone do not cause non-zero exit."""
        bib_file = tmp_path / "refs.bib"
        bib_file.write_text(textwrap.dedent("""\
            @article{Test2020,
              author  = {Author, A},
              title   = {Test},
              journal = {J},
              year    = {2020},
            }
        """))
        rc = cv.main(["--input", str(bib_file)])
        assert rc == 0

    def test_errors_always_fail(self, tmp_path):
        """Errors cause non-zero exit even without --strict."""
        bib_file = tmp_path / "refs.bib"
        # Missing required author field
        bib_file.write_text(textwrap.dedent("""\
            @article{Bad2020,
              title   = {Test},
              journal = {J},
              year    = {2020},
              doi     = {10.1/x},
            }
        """))
        rc = cv.main(["--input", str(bib_file)])
        assert rc == 1

    def test_file_not_found(self):
        """Non-existent file returns exit code 2."""
        rc = cv.main(["--input", "/tmp/nonexistent_file_12345.bib"])
        assert rc == 2

    def test_no_entries_returns_error(self, tmp_path):
        """A file with no BibTeX entries returns exit code 1."""
        bib_file = tmp_path / "empty.bib"
        bib_file.write_text("% This file has no entries\n")
        rc = cv.main(["--input", str(bib_file)])
        assert rc == 1


class TestValidatorMalformed:
    """Tests for handling malformed BibTeX input."""

    def test_unclosed_brace_still_parses(self):
        """Parser handles unclosed braces gracefully (best-effort)."""
        bib = textwrap.dedent("""\
            @article{Broken2020,
              author = {Author, A},
              title  = {This brace is never closed,
              journal = {J},
              year   = {2020},
            }
        """)
        # Should not crash; may or may not parse all fields
        entries = cv.parse_bib(bib)
        assert isinstance(entries, list)

    def test_entry_with_quoted_values(self):
        """Fields delimited with double quotes are parsed."""
        bib = textwrap.dedent("""\
            @article{Quoted2020,
              author  = "Author, A",
              title   = "A Quoted Title",
              journal = "J. of Testing",
              year    = "2020",
              doi     = "10.1000/test",
            }
        """)
        entries = cv.parse_bib(bib)
        assert len(entries) == 1
        assert entries[0].fields["title"] == "A Quoted Title"

    def test_bare_numeric_year(self):
        """A bare numeric year (no braces/quotes) is parsed."""
        bib = textwrap.dedent("""\
            @article{Bare2020,
              author  = {Author, A},
              title   = {Test},
              journal = {J},
              year    = 2020,
              doi     = {10.1/x},
            }
        """)
        entries = cv.parse_bib(bib)
        assert len(entries) == 1
        assert entries[0].fields["year"] == "2020"
