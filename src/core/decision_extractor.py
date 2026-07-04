"""
Decision Extractor Agent.

Reads raw meeting notes from session state and extracts all decisions,
requirements, constraints, and open questions — each with source evidence.

Input state key:  "raw_notes"
Output state key: "extraction"  (serialised ExtractionOutput JSON)
"""

from __future__ import annotations

import json
from pathlib import Path

from google.adk.agents import LlmAgent

from src.schemas.models import ExtractionOutput

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "decision_extractor.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _build_instruction() -> str:
    return (
        _SYSTEM_PROMPT
        + "\n\n"
        + "Meeting notes to analyse:\n\n{raw_notes}"
    )


decision_extractor = LlmAgent(
    name="decision_extractor",
    model="gemini-2.5-flash",
    instruction=_build_instruction(),
    description=(
        "Extracts all decisions, requirements, constraints, and open questions "
        "from raw meeting notes. Every extracted item includes source evidence."
    ),
    output_schema=ExtractionOutput,
    output_key="extraction",
)
