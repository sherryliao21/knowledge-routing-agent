"""
Parser module — pure Python, no LLM.

Reads a Markdown meeting notes file, validates it (security: file type +
size cap), and returns the raw text for the pipeline.

Raw text is ONLY passed through the pipeline as session state. It is
never written to any output file.
"""

from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass

# Security: reject inputs larger than 50,000 characters (~10 pages of dense text)
MAX_INPUT_CHARS = 50_000


class ParserError(Exception):
    """Raised when the input file fails validation."""


@dataclass
class ParsedDocument:
    """Result of parsing a meeting notes file."""

    title: str
    """Human-readable title (from --title CLI flag or filename)."""

    date: str
    """Meeting date in YYYY-MM-DD format (from --date CLI flag)."""

    run_id: str
    """URL-safe slug used as the output folder name, e.g. '2026-07-01-planning'."""

    source_filename: str
    """Original input file basename (e.g. '2026-07-01-planning.md')."""

    raw_text: str
    """
    The raw meeting notes text.

    SECURITY NOTE: This field is used only within the agent pipeline.
    It must NEVER be written to any output file (output.json, source-map.json,
    or any HTML report). Only extracted/summarized content is persisted.
    """

    char_count: int
    """Total character count of the raw text."""


def _slugify(text: str) -> str:
    """Convert a string to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def parse_meeting_notes(
    file_path: str | Path,
    title: str,
    date: str,
) -> ParsedDocument:
    """
    Read and validate a Markdown meeting notes file.

    Args:
        file_path: Path to the .md file.
        title: Human-readable title for this run (from CLI --title flag).
        date: Meeting date in YYYY-MM-DD format (from CLI --date flag).

    Returns:
        ParsedDocument with validated content.

    Raises:
        ParserError: If the file fails any security or format validation.
    """
    path = Path(file_path)

    # Security check 1: must be a .md file
    if path.suffix.lower() != ".md":
        raise ParserError(
            f"Invalid file type '{path.suffix}'. Only Markdown (.md) files are accepted.\n"
            f"Tip: Save your meeting notes as a .md file and try again."
        )

    # Existence check
    if not path.exists():
        raise ParserError(f"File not found: {path}")

    if not path.is_file():
        raise ParserError(f"Path is not a file: {path}")

    # Read content
    try:
        raw_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ParserError(
            f"Could not read '{path.name}' as UTF-8 text. "
            "Please ensure the file is saved with UTF-8 encoding."
        )

    # Security check 2: enforce size cap
    if len(raw_text) > MAX_INPUT_CHARS:
        raise ParserError(
            f"File too large: {len(raw_text):,} characters "
            f"(maximum is {MAX_INPUT_CHARS:,}).\n"
            f"Tip: Split long documents into separate meeting note files."
        )

    # Reject empty files
    stripped = raw_text.strip()
    if not stripped:
        raise ParserError(f"File '{path.name}' is empty.")

    # Build run_id from date + title slug
    title_slug = _slugify(title) if title else _slugify(path.stem)
    run_id = f"{date}-{title_slug}" if date else title_slug

    return ParsedDocument(
        title=title,
        date=date,
        run_id=run_id,
        source_filename=path.name,
        raw_text=stripped,
        char_count=len(stripped),
    )
