"""
Role Router Agents — run in parallel via ParallelAgent.

Each agent reads the same extracted decisions from session state and
produces a role-specific view of the information.

Input state key:  "extraction"  (ExtractionOutput JSON from decision_extractor)
Output state keys:
  "engineer_view"    → EngineerView
  "qa_view"          → QAView
  "pm_view"          → PMView
  "stakeholder_view" → StakeholderView
"""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent, ParallelAgent

from src.schemas.models import EngineerView, QAView, PMView, StakeholderView

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def _build_instruction(prompt: str) -> str:
    return (
        prompt
        + "\n\n"
        + "Extracted decisions (JSON):\n\n{extraction}"
    )


# --- Individual role agents ---------------------------------------------------

engineer_router = LlmAgent(
    name="engineer_router",
    model="gemini-2.5-flash",
    instruction=_build_instruction(_load_prompt("engineer_router")),
    description="Produces an engineer-specific view of the extracted decisions.",
    output_schema=EngineerView,
    output_key="engineer_view",
)

qa_router = LlmAgent(
    name="qa_router",
    model="gemini-2.5-flash",
    instruction=_build_instruction(_load_prompt("qa_router")),
    description="Produces a QA-specific view with acceptance criteria and test scenarios.",
    output_schema=QAView,
    output_key="qa_view",
)

pm_router = LlmAgent(
    name="pm_router",
    model="gemini-2.5-flash",
    instruction=_build_instruction(_load_prompt("pm_router")),
    description="Produces a PM/SA view covering decisions, dependencies, risks, and gaps.",
    output_schema=PMView,
    output_key="pm_view",
)

stakeholder_router = LlmAgent(
    name="stakeholder_router",
    model="gemini-2.5-flash",
    instruction=_build_instruction(_load_prompt("stakeholder_router")),
    description="Produces a plain-language stakeholder summary.",
    output_schema=StakeholderView,
    output_key="stakeholder_view",
)

# --- Parallel wrapper ---------------------------------------------------------

role_router = ParallelAgent(
    name="role_router",
    description=(
        "Runs all four role routers in parallel: engineer, QA, PM, and stakeholder."
    ),
    sub_agents=[engineer_router, qa_router, pm_router, stakeholder_router],
)
