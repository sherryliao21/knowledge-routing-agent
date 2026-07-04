"""
Reviewer Agent.

Performs two checks on the pipeline output before the report is published:
  1. Hallucination check — every claim must trace back to an extracted decision
  2. Quality check — outputs must be useful and ready to share

Input state keys: "extraction", "engineer_view", "qa_view", "pm_view", "stakeholder_view"
Output state key: "review"  (ReviewOutput JSON)
"""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent

from src.schemas.models import ReviewOutput

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "reviewer.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _build_instruction() -> str:
    return (
        _SYSTEM_PROMPT
        + "\n\n"
        + "## Extracted Decisions\n\n{extraction}"
        + "\n\n"
        + "## Engineer View\n\n{engineer_view}"
        + "\n\n"
        + "## QA View\n\n{qa_view}"
        + "\n\n"
        + "## PM View\n\n{pm_view}"
        + "\n\n"
        + "## Stakeholder View\n\n{stakeholder_view}"
    )


reviewer = LlmAgent(
    name="reviewer",
    model="gemini-2.5-flash",
    instruction=_build_instruction(),
    description=(
        "Reviews all pipeline outputs for hallucinations and quality issues "
        "before the report is published. Returns PASS or NEEDS_IMPROVEMENT."
    ),
    output_schema=ReviewOutput,
    output_key="review",
)
