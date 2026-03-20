"""Conversion engine: markdown to docx and LaTeX."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def _parse_markdown(md_text: str) -> list[dict]:
    """Parse markdown into a list of block elements.

    Each block is a dict with 'type' and relevant fields.
    Types: heading, paragraph, table, code_block, blank
    """
    blocks: list[dict] = []
    lines = md_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code block (fenced)
        if line.strip().startswith("```"):
            lang = line.strip().removeprefix("```").strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({"type": "code_block", "lang": lang, "content": "\n".join(code_lines)})
            i += 1  # skip closing ```
            continue

        # Heading
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            blocks.append({"type": "heading", "level": level, "text": text})
            i += 1
            continue

        # Table (starts with |)
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\|[\s\-:|]+\|$", lines[i + 1].strip()
        ):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            blocks.append({"type": "table", "lines": table_lines})
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph (collect consecutive non-blank, non-special lines)
        para_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("#") and not lines[i].strip().startswith("```") and not lines[i].strip().startswith("|"):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            blocks.append({"type": "paragraph", "text": " ".join(para_lines)})

    return blocks


def _parse_table_lines(table_lines: list[str]) -> tuple[list[str], list[list[str]]]:
    """Parse markdown table lines into headers and rows."""
    def split_row(line: str) -> list[str]:
        line = line.strip().strip("|")
        return [cell.strip() for cell in line.split("|")]

    headers = split_row(table_lines[0])
    # Skip separator line (index 1)
    rows = [split_row(line) for line in table_lines[2:]]
    return headers, rows


def _add_inline_formatting(run_adder, text: str) -> None:
    """Parse inline bold/italic and add formatted runs.

    run_adder is a callable(text, bold, italic) that adds a run.
    """
    # Pattern: **bold**, *italic*, ***bold+italic***
    pattern = re.compile(r"(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*)")
    last_end = 0
    for m in pattern.finditer(text):
        # Add text before this match
        if m.start() > last_end:
            run_adder(text[last_end : m.start()], False, False)
        if m.group(2):  # ***bold+italic***
            run_adder(m.group(2), True, True)
        elif m.group(3):  # **bold**
            run_adder(m.group(3), True, False)
        elif m.group(4):  # *italic*
            run_adder(m.group(4), False, True)
        last_end = m.end()
    if last_end < len(text):
        run_adder(text[last_end:], False, False)


def markdown_to_docx(
    md_path: str, output_path: str, template_path: str | None = None
) -> str:
    """Convert a markdown file to a Word (.docx) document.

    Args:
        md_path: Path to source markdown file.
        output_path: Path for the output .docx file.
        template_path: Optional path to a .docx template for styles.

    Returns:
        The output path of the created document.
    """
    md_path = Path(md_path)
    output_path = Path(output_path)

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    md_text = md_path.read_text(encoding="utf-8")
    blocks = _parse_markdown(md_text)

    # Create document from template or blank
    if template_path and Path(template_path).exists():
        doc = Document(template_path)
    else:
        doc = Document()

    # Style mapping: H1 → Title, H2 → Heading 1, H3 → Heading 2, etc.
    heading_style_map = {
        1: "Title",
        2: "Heading 1",
        3: "Heading 2",
        4: "Heading 3",
        5: "Heading 4",
        6: "Heading 5",
    }

    for block in blocks:
        if block["type"] == "heading":
            level = block["level"]
            style = heading_style_map.get(level, "Heading 5")
            doc.add_heading(block["text"], level=0 if level == 1 else level - 1)

        elif block["type"] == "paragraph":
            para = doc.add_paragraph()
            _add_inline_formatting(
                lambda t, b, it, p=para: _add_run(p, t, b, it),
                block["text"],
            )

        elif block["type"] == "code_block":
            para = doc.add_paragraph()
            para.style = doc.styles["Normal"]
            run = para.add_run(block["content"])
            run.font.name = "Courier New"
            run.font.size = Pt(9)

        elif block["type"] == "table":
            headers, rows = _parse_table_lines(block["lines"])
            num_cols = len(headers)
            table = doc.add_table(rows=1, cols=num_cols)
            table.style = "Table Grid"

            # Header row
            for j, header in enumerate(headers):
                cell = table.rows[0].cells[j]
                cell.text = header
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True

            # Data rows
            for row_data in rows:
                row = table.add_row()
                for j, cell_text in enumerate(row_data):
                    if j < num_cols:
                        row.cells[j].text = cell_text

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    return str(output_path)


def _add_run(paragraph, text: str, bold: bool, italic: bool) -> None:
    """Add a formatted run to a paragraph."""
    run = paragraph.add_run(text)
    if bold:
        run.bold = True
    if italic:
        run.italic = True


def markdown_to_latex(
    md_path: str, output_path: str, template_path: str | None = None
) -> str:
    """Convert a markdown file to LaTeX (.tex).

    Args:
        md_path: Path to source markdown file.
        output_path: Path for the output .tex file.
        template_path: Optional path to a .tex template file.

    Returns:
        The output path of the created document.
    """
    md_path = Path(md_path)
    output_path = Path(output_path)

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    md_text = md_path.read_text(encoding="utf-8")
    blocks = _parse_markdown(md_text)

    # Determine document class from template or default
    preamble = ""
    if template_path and Path(template_path).exists():
        preamble = Path(template_path).read_text(encoding="utf-8")
    else:
        preamble = (
            "\\documentclass{article}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\usepackage{graphicx}\n"
            "\\usepackage{booktabs}\n"
            "\\usepackage{hyperref}\n"
        )

    body_parts: list[str] = []

    heading_cmd_map = {
        1: "section",
        2: "subsection",
        3: "subsubsection",
        4: "paragraph",
        5: "subparagraph",
        6: "subparagraph",
    }

    for block in blocks:
        if block["type"] == "heading":
            cmd = heading_cmd_map.get(block["level"], "subparagraph")
            body_parts.append(f"\\{cmd}{{{_latex_escape_inline(block['text'])}}}")

        elif block["type"] == "paragraph":
            body_parts.append(_convert_inline_to_latex(block["text"]))
            body_parts.append("")  # blank line for paragraph break

        elif block["type"] == "code_block":
            body_parts.append("\\begin{verbatim}")
            body_parts.append(block["content"])
            body_parts.append("\\end{verbatim}")

        elif block["type"] == "table":
            headers, rows = _parse_table_lines(block["lines"])
            col_spec = " ".join(["l"] * len(headers))
            body_parts.append(f"\\begin{{tabular}}{{{col_spec}}}")
            body_parts.append("\\toprule")
            body_parts.append(" & ".join(_latex_escape(h) for h in headers) + " \\\\")
            body_parts.append("\\midrule")
            for row_data in rows:
                # Pad row to match header count
                padded = row_data + [""] * (len(headers) - len(row_data))
                body_parts.append(
                    " & ".join(_latex_escape(c) for c in padded[: len(headers)]) + " \\\\"
                )
            body_parts.append("\\bottomrule")
            body_parts.append("\\end{tabular}")

    # Assemble full document
    latex_content = preamble + "\n\\begin{document}\n\n" + "\n".join(body_parts) + "\n\n\\end{document}\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(latex_content, encoding="utf-8")
    return str(output_path)


def _latex_escape(text: str) -> str:
    """Escape special LaTeX characters."""
    replacements = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def _latex_escape_inline(text: str) -> str:
    """Escape LaTeX chars but preserve citation commands."""
    # Preserve \cite{...} markers
    citations = re.findall(r"\\cite\{[^}]+\}", text)
    for i, cite in enumerate(citations):
        text = text.replace(cite, f"__CITE_{i}__")

    text = _latex_escape(text)

    for i, cite in enumerate(citations):
        text = text.replace(f"__CITE_{i}__", cite)

    return text


def _convert_inline_to_latex(text: str) -> str:
    """Convert markdown inline formatting to LaTeX."""
    # Preserve \cite{} before escaping
    citations = re.findall(r"\\cite\{[^}]+\}", text)
    for i, cite in enumerate(citations):
        text = text.replace(cite, f"__CITE_{i}__")

    # Bold+italic: ***text*** → \textbf{\textit{text}}
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"__BOLDITALIC_START__\1__BOLDITALIC_END__", text)
    # Bold: **text** → \textbf{text}
    text = re.sub(r"\*\*(.+?)\*\*", r"__BOLD_START__\1__BOLD_END__", text)
    # Italic: *text* → \textit{text}
    text = re.sub(r"\*(.+?)\*", r"__ITALIC_START__\1__ITALIC_END__", text)

    text = _latex_escape(text)

    text = text.replace("__BOLDITALIC_START__", "\\textbf{\\textit{")
    text = text.replace("__BOLDITALIC_END__", "}}")
    text = text.replace("__BOLD_START__", "\\textbf{")
    text = text.replace("__BOLD_END__", "}")
    text = text.replace("__ITALIC_START__", "\\textit{")
    text = text.replace("__ITALIC_END__", "}")

    for i, cite in enumerate(citations):
        text = text.replace(f"\\_\\_CITE\\_{i}\\_\\_", cite)

    return text
