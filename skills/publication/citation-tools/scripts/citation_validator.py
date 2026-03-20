#!/usr/bin/env python3
"""Validate a BibTeX (.bib) file for common issues.

Checks for missing required fields, duplicate citation keys, entries
without a DOI, year format problems, and encoding issues.  Uses only
the Python standard library (re) for BibTeX parsing -- no external
dependencies required.

Examples
--------
    # Basic validation
    python citation_validator.py --input references.bib

    # Strict mode: exit non-zero on warnings too
    python citation_validator.py --input references.bib --strict
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import TextIO

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class Severity(Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class Issue:
    """A single validation issue."""

    severity: Severity
    entry_key: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.entry_key}: {self.message}"


@dataclass
class BibEntry:
    """Parsed BibTeX entry."""

    entry_type: str = ""
    cite_key: str = ""
    fields: dict[str, str] = field(default_factory=dict)
    line_number: int = 0


# ---------------------------------------------------------------------------
# Simple BibTeX parser
# ---------------------------------------------------------------------------

# Matches the opening of an entry: @type{key,
_ENTRY_START = re.compile(
    r"@\s*(\w+)\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE
)

# Types that are not actual reference entries
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
    """Parse ``key = {value}`` pairs from the body of a BibTeX entry.

    This is intentionally simple.  It handles:
      - Values wrapped in braces ``{...}`` (including nested braces)
      - Values wrapped in double quotes ``"..."``
      - Bare numeric values
    """
    fields: dict[str, str] = {}
    pos = 0
    length = len(body)

    while pos < length:
        # Find the next '='
        eq_match = re.search(r"(\w[\w\-]*)\s*=\s*", body[pos:])
        if not eq_match:
            break
        key = eq_match.group(1).lower()
        val_start = pos + eq_match.end()

        # Determine value delimiter
        if val_start >= length:
            break

        ch = body[val_start]
        if ch == "{":
            # Find matching closing brace
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
                # Unmatched brace -- take everything
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
            # Bare value (number or string macro) -- up to comma or end
            comma = body.find(",", val_start)
            if comma == -1:
                fields[key] = body[val_start:].strip().rstrip("}")
                break
            fields[key] = body[val_start:comma].strip()
            pos = comma + 1
            continue

        # Skip optional comma
        while pos < length and body[pos] in (" ", "\t", "\n", "\r", ","):
            pos += 1

    return fields


def parse_bib(text: str) -> list[BibEntry]:
    """Parse *text* as BibTeX and return a list of :class:`BibEntry`."""
    entries: list[BibEntry] = []

    for m in _ENTRY_START.finditer(text):
        entry_type = m.group(1).lower()
        if entry_type in _NON_ENTRY_TYPES:
            continue

        cite_key = m.group(2)
        # Determine line number of this entry
        line_number = text[: m.start()].count("\n") + 1

        # Find the matching closing brace for the entry
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

        entries.append(
            BibEntry(
                entry_type=entry_type,
                cite_key=cite_key,
                fields=fields,
                line_number=line_number,
            )
        )

    return entries


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

# Required fields per entry type (minimal set -- not the full BibTeX spec).
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


def validate(entries: list[BibEntry]) -> list[Issue]:
    """Run all validation checks and return a list of issues."""
    issues: list[Issue] = []
    seen_keys: dict[str, int] = {}

    for entry in entries:
        key = entry.cite_key

        # -- Duplicate keys --
        if key in seen_keys:
            issues.append(Issue(
                Severity.ERROR,
                key,
                f"Duplicate citation key (first seen at line {seen_keys[key]}, "
                f"duplicate at line {entry.line_number})",
            ))
        else:
            seen_keys[key] = entry.line_number

        # -- Missing required fields --
        required = REQUIRED_FIELDS.get(entry.entry_type, ["author", "title", "year"])
        for rf in required:
            if rf not in entry.fields or not entry.fields[rf].strip():
                issues.append(Issue(
                    Severity.ERROR,
                    key,
                    f"Missing required field '{rf}' for @{entry.entry_type}",
                ))

        # -- Year format --
        year_val = entry.fields.get("year", "")
        if year_val and not re.fullmatch(r"\d{4}", year_val.strip()):
            issues.append(Issue(
                Severity.WARNING,
                key,
                f"Year field has unexpected format: '{year_val}' (expected YYYY)",
            ))

        # -- Missing DOI --
        if "doi" not in entry.fields or not entry.fields["doi"].strip():
            issues.append(Issue(
                Severity.WARNING,
                key,
                "No DOI field present",
            ))

        # -- Encoding: detect common mojibake / raw LaTeX remnants --
        for fname, fval in entry.fields.items():
            if re.search(r"[\x80-\x9f]", fval):
                issues.append(Issue(
                    Severity.WARNING,
                    key,
                    f"Possible encoding issue in field '{fname}' "
                    f"(contains control characters in 0x80-0x9F range)",
                ))

        # -- Empty fields --
        for fname, fval in entry.fields.items():
            if fval.strip() == "":
                issues.append(Issue(
                    Severity.WARNING,
                    key,
                    f"Field '{fname}' is present but empty",
                ))

    return issues


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _print_report(
    entries: list[BibEntry],
    issues: list[Issue],
    out: TextIO = sys.stdout,
) -> None:
    """Print a human-readable validation report."""
    errors = [i for i in issues if i.severity is Severity.ERROR]
    warnings = [i for i in issues if i.severity is Severity.WARNING]

    out.write(f"Parsed {len(entries)} entries.\n")
    out.write(f"Found {len(errors)} error(s) and {len(warnings)} warning(s).\n")

    if not issues:
        out.write("No issues found.\n")
        return

    out.write("\n")
    if errors:
        out.write("--- Errors ---\n")
        for issue in errors:
            out.write(f"  {issue}\n")
        out.write("\n")
    if warnings:
        out.write("--- Warnings ---\n")
        for issue in warnings:
            out.write(f"  {issue}\n")
        out.write("\n")

    # Summary by entry
    affected: dict[str, list[Issue]] = {}
    for issue in issues:
        affected.setdefault(issue.entry_key, []).append(issue)
    clean = len(entries) - len(affected)
    out.write(
        f"Summary: {clean}/{len(entries)} entries are clean, "
        f"{len(affected)} have issues.\n"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a .bib file for common citation issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              %(prog)s --input references.bib
              %(prog)s --input references.bib --strict
        """),
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the .bib file to validate.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with non-zero status on warnings (not just errors).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        with open(args.input, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: Could not read file: {exc}", file=sys.stderr)
        return 2

    entries = parse_bib(text)
    if not entries:
        print(f"No BibTeX entries found in {args.input}.", file=sys.stderr)
        return 1

    issues = validate(entries)
    _print_report(entries, issues)

    errors = any(i.severity is Severity.ERROR for i in issues)
    warnings = any(i.severity is Severity.WARNING for i in issues)

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
