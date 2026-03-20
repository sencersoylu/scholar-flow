"""BibTeX parsing, formatting, and validation utilities."""

from __future__ import annotations

import re

from citation_mcp.models import Reference, ValidationIssue

# ---------------------------------------------------------------------------
# BibTeX parser (adapted from citation_validator.py)
# ---------------------------------------------------------------------------

_ENTRY_START = re.compile(r"@\s*(\w+)\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
_NON_ENTRY_TYPES = {"string", "preamble", "comment"}


def _parse_field_value(raw: str) -> str:
    """Strip outer braces / quotes from a BibTeX field value."""
    raw = raw.strip()
    if raw.startswith("{") and raw.endswith("}"):
        raw = raw[1:-1]
    elif raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1]
    return raw.strip()


def _extract_fields(body: str) -> dict[str, str]:
    """Parse key = {value} pairs from the body of a BibTeX entry."""
    fields: dict[str, str] = {}
    pos = 0
    length = len(body)

    while pos < length:
        eq_match = re.search(r"(\w[\w\-]*)\s*=\s*", body[pos:])
        if not eq_match:
            break
        key = eq_match.group(1).lower()
        val_start = pos + eq_match.end()

        if val_start >= length:
            break

        ch = body[val_start]
        if ch == "{":
            depth = 0
            i = val_start
            while i < length:
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                    if depth == 0:
                        fields[key] = _parse_field_value(body[val_start : i + 1])
                        pos = i + 1
                        break
                i += 1
            else:
                fields[key] = _parse_field_value(body[val_start:])
                break
        elif ch == '"':
            end = body.find('"', val_start + 1)
            if end == -1:
                fields[key] = _parse_field_value(body[val_start:])
                break
            fields[key] = _parse_field_value(body[val_start : end + 1])
            pos = end + 1
        else:
            comma = body.find(",", val_start)
            if comma == -1:
                fields[key] = body[val_start:].strip().rstrip("}")
                break
            fields[key] = body[val_start:comma].strip()
            pos = comma + 1
            continue

        while pos < length and body[pos] in (" ", "\t", "\n", "\r", ","):
            pos += 1

    return fields


def parse_bibtex(text: str) -> list[Reference]:
    """Parse BibTeX text into a list of Reference objects."""
    references: list[Reference] = []

    for m in _ENTRY_START.finditer(text):
        entry_type = m.group(1).lower()
        if entry_type in _NON_ENTRY_TYPES:
            continue

        cite_key = m.group(2)

        # Find matching closing brace
        start = m.end()
        depth = 1
        i = start
        length = len(text)
        while i < length and depth > 0:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        body = text[start : i - 1] if depth == 0 else text[start:]

        fields = _extract_fields(body)

        # Parse authors from BibTeX "and"-separated format
        authors: list[str] = []
        author_str = fields.get("author", "")
        if author_str:
            authors = [a.strip() for a in author_str.split(" and ") if a.strip()]

        references.append(
            Reference(
                doi=fields.get("doi", ""),
                title=fields.get("title", ""),
                authors=authors,
                year=fields.get("year", ""),
                journal=fields.get("journal", fields.get("booktitle", "")),
                volume=fields.get("volume", ""),
                issue=fields.get("number", ""),
                pages=fields.get("pages", ""),
                bibtex_key=cite_key,
                entry_type=entry_type,
            )
        )

    return references


# ---------------------------------------------------------------------------
# BibTeX formatter
# ---------------------------------------------------------------------------


def format_bibtex(ref: Reference) -> str:
    """Format a Reference as a BibTeX entry string."""
    fields: list[tuple[str, str]] = []

    if ref.authors:
        fields.append(("author", " and ".join(ref.authors)))

    if ref.title:
        fields.append(("title", "{" + ref.title + "}"))

    if ref.journal:
        field_name = "journal" if ref.entry_type == "article" else "booktitle"
        fields.append((field_name, ref.journal))

    if ref.year:
        fields.append(("year", ref.year))

    if ref.volume:
        fields.append(("volume", ref.volume))

    if ref.issue:
        fields.append(("number", ref.issue))

    if ref.pages:
        fields.append(("pages", ref.pages))

    if ref.doi:
        fields.append(("doi", ref.doi))

    if not fields:
        return f"@{ref.entry_type}{{{ref.bibtex_key},\n}}"

    max_key_len = max(len(k) for k, _ in fields)
    lines = [f"@{ref.entry_type}{{{ref.bibtex_key},"]
    for key, value in fields:
        padding = " " * (max_key_len - len(key))
        lines.append(f"  {key}{padding} = {{{value}}},")
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# BibTeX validator (adapted from citation_validator.py)
# ---------------------------------------------------------------------------

REQUIRED_FIELDS: dict[str, list[str]] = {
    "article": ["author", "title", "journal", "year"],
    "book": ["author", "title", "publisher", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "incollection": ["author", "title", "booktitle", "year"],
    "phdthesis": ["author", "title", "school", "year"],
    "mastersthesis": ["author", "title", "school", "year"],
    "techreport": ["author", "title", "institution", "year"],
    "misc": ["title"],
}


def validate_bibtex(text: str) -> list[ValidationIssue]:
    """Validate BibTeX text and return a list of issues."""
    issues: list[ValidationIssue] = []
    seen_keys: dict[str, bool] = {}

    # Re-parse at a lower level to get fields for validation
    for m in _ENTRY_START.finditer(text):
        entry_type = m.group(1).lower()
        if entry_type in _NON_ENTRY_TYPES:
            continue

        cite_key = m.group(2)

        # Find matching closing brace
        start = m.end()
        depth = 1
        i = start
        length = len(text)
        while i < length and depth > 0:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        body = text[start : i - 1] if depth == 0 else text[start:]
        fields = _extract_fields(body)

        # Duplicate keys
        if cite_key in seen_keys:
            issues.append(
                ValidationIssue(
                    severity="error",
                    entry_key=cite_key,
                    message="Duplicate citation key",
                )
            )
        else:
            seen_keys[cite_key] = True

        # Missing required fields
        required = REQUIRED_FIELDS.get(entry_type, ["author", "title", "year"])
        for rf in required:
            if rf not in fields or not fields[rf].strip():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        entry_key=cite_key,
                        message=f"Missing required field '{rf}' for @{entry_type}",
                    )
                )

        # Year format
        year_val = fields.get("year", "")
        if year_val and not re.fullmatch(r"\d{4}", year_val.strip()):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    entry_key=cite_key,
                    message=f"Year field has unexpected format: '{year_val}' (expected YYYY)",
                )
            )

        # Missing DOI
        if "doi" not in fields or not fields["doi"].strip():
            issues.append(
                ValidationIssue(
                    severity="warning",
                    entry_key=cite_key,
                    message="No DOI field present",
                )
            )

        # Empty fields
        for fname, fval in fields.items():
            if fval.strip() == "":
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        entry_key=cite_key,
                        message=f"Field '{fname}' is present but empty",
                    )
                )

        # Encoding issues
        for fname, fval in fields.items():
            if re.search(r"[\x80-\x9f]", fval):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        entry_key=cite_key,
                        message=f"Possible encoding issue in field '{fname}'",
                    )
                )

    return issues
