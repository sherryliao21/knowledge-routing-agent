"""
Pydantic data schemas for the Knowledge Routing Agent.

These models define the contracts between every stage of the pipeline:
  Parser → DecisionExtractor → RoleRouter → Reviewer → ReportBuilder

All inter-agent state is typed here. No agent writes freeform strings to
session state — only these structured objects.
"""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Source Evidence
# ---------------------------------------------------------------------------


class SourceEvidence(BaseModel):
    """A verbatim quote from the original meeting notes that supports a claim.

    Every extracted decision or claim must reference at least one piece of
    source evidence. If no clear evidence exists, the claim must be labeled
    as 'inferred_needs_confirmation'.
    """

    quote: str = Field(
        description="Verbatim excerpt from the original meeting notes."
    )
    approximate_location: str = Field(
        description=(
            "Rough location in the source document, e.g. 'paragraph 3' "
            "or 'under heading: Login Module'."
        )
    )


# ---------------------------------------------------------------------------
# Extracted Decisions & Claims
# ---------------------------------------------------------------------------


ConfidenceLevel = Literal["confirmed", "inferred_needs_confirmation"]


class SourcedDecision(BaseModel):
    """A single decision, requirement, or constraint extracted from the notes.

    The 'confidence' field is the core trust signal:
    - 'confirmed': clearly stated in the source with direct evidence.
    - 'inferred_needs_confirmation': implied or ambiguous — must be flagged
      for human review before being treated as a confirmed decision.
    """

    id: str = Field(description="Unique short ID, e.g. 'D001', 'D002'.")
    title: str = Field(description="One-line summary of the decision or claim.")
    detail: str = Field(description="Full explanation of the decision or constraint.")
    category: Literal[
        "business_requirement",
        "functional_requirement",
        "technical_constraint",
        "key_decision",
        "open_question",
        "deadline_or_milestone",
        "risk",
        "dependency",
    ] = Field(description="Category of this item.")
    confidence: ConfidenceLevel = Field(
        description=(
            "Set to 'confirmed' only when backed by direct source evidence. "
            "Otherwise use 'inferred_needs_confirmation'."
        )
    )
    evidence: list[SourceEvidence] = Field(
        default_factory=list,
        description=(
            "Source quotes supporting this decision. Empty list is only "
            "allowed when confidence is 'inferred_needs_confirmation'."
        ),
    )


class ExtractionOutput(BaseModel):
    """Output of the DecisionExtractor agent stage."""

    decisions: list[SourcedDecision] = Field(
        description="All extracted decisions, requirements, and constraints."
    )
    total_confirmed: int = Field(
        description="Count of decisions with confidence='confirmed'."
    )
    total_inferred: int = Field(
        description="Count of decisions with confidence='inferred_needs_confirmation'."
    )


# ---------------------------------------------------------------------------
# Source Map (for output.json + source-map.json)
# ---------------------------------------------------------------------------


class SourceMapEntry(BaseModel):
    """Maps a decision ID to its source evidence. Written to source-map.json."""

    decision_id: str
    decision_title: str
    confidence: ConfidenceLevel
    evidence_quotes: list[str] = Field(
        description="Verbatim quotes from the original notes."
    )


# ---------------------------------------------------------------------------
# Role-Specific Views
# ---------------------------------------------------------------------------


class EngineerView(BaseModel):
    """Role output tailored for a software engineer."""

    implementation_scope: list[str] = Field(
        description="Concrete features or components to build."
    )
    technical_constraints: list[str] = Field(
        description="Technical limitations, stack decisions, or non-negotiables."
    )
    relevant_decisions: list[str] = Field(
        description="Decision IDs relevant to engineering work."
    )
    open_technical_questions: list[str] = Field(
        description="Unresolved technical questions that block implementation."
    )


class QAView(BaseModel):
    """Role output tailored for a QA engineer."""

    acceptance_criteria: list[str] = Field(
        description="Measurable, testable conditions for each feature."
    )
    test_scenarios: list[str] = Field(
        description="Key test cases to validate the implementation."
    )
    edge_cases: list[str] = Field(
        description="Boundary conditions and unusual inputs to consider."
    )
    unresolved_behaviors: list[str] = Field(
        description="Behaviors that are unclear and need clarification before testing."
    )


class PMView(BaseModel):
    """Role output tailored for a Project Manager or System Analyst."""

    decision_history: list[str] = Field(
        description="Chronological summary of decisions made in the meeting."
    )
    dependencies: list[str] = Field(
        description="Cross-team, cross-system, or cross-feature dependencies."
    )
    risks: list[str] = Field(
        description="Identified risks and their potential impact."
    )
    alignment_gaps: list[str] = Field(
        description="Areas where stakeholders may not be aligned."
    )
    open_questions: list[str] = Field(
        description="Questions that must be resolved before work can proceed."
    )


class StakeholderView(BaseModel):
    """Role output tailored for a non-technical stakeholder."""

    business_summary: str = Field(
        description="2–3 sentence plain-language summary of what was discussed."
    )
    key_impact: list[str] = Field(
        description="How these decisions affect the business or end users."
    )
    decisions_needing_alignment: list[str] = Field(
        description="Decisions that still need stakeholder sign-off."
    )
    major_unresolved_questions: list[str] = Field(
        description="The most important open questions in plain language."
    )


class RoleOutputs(BaseModel):
    """All four role-specific views, produced in parallel."""

    engineer: EngineerView
    qa: QAView
    pm: PMView
    stakeholder: StakeholderView


# ---------------------------------------------------------------------------
# Reviewer Output
# ---------------------------------------------------------------------------


class ReviewIssue(BaseModel):
    """A single quality issue flagged by the Reviewer agent."""

    severity: Literal["critical", "warning", "info"] = Field(
        description=(
            "'critical' = blocks publishing (hallucination or missing source). "
            "'warning' = should fix before sharing. "
            "'info' = minor suggestion."
        )
    )
    location: str = Field(
        description="Which role view or decision ID this issue refers to."
    )
    description: str = Field(description="What the issue is.")
    suggestion: str = Field(description="How to fix or flag it.")


class ReviewOutput(BaseModel):
    """Output of the Reviewer agent stage."""

    status: Literal["PASS", "NEEDS_IMPROVEMENT"] = Field(
        description=(
            "PASS = quality is sufficient to publish the report. "
            "NEEDS_IMPROVEMENT = critical issues must be addressed."
        )
    )
    issues: list[ReviewIssue] = Field(
        default_factory=list,
        description="List of issues found. Empty if status is PASS.",
    )
    reviewer_notes: str = Field(
        description="Brief overall summary of the review findings."
    )


# ---------------------------------------------------------------------------
# Run Output (top-level, written to output.json)
# ---------------------------------------------------------------------------


class RunMetadata(BaseModel):
    """Metadata about this pipeline run."""

    title: str = Field(description="Human-readable title for this run.")
    date: str = Field(description="Date of the meeting notes, YYYY-MM-DD format.")
    run_id: str = Field(description="Slug used as the folder name, e.g. '2026-07-01-planning'.")
    source_file: str = Field(description="Original input filename (basename only, not full path).")
    generated_at: str = Field(description="ISO 8601 timestamp when the report was generated.")


class RunOutput(BaseModel):
    """
    Complete output of one pipeline run. Written to output.json.

    IMPORTANT: This object does NOT contain the raw meeting notes.
    Only extracted, summarized content is persisted — never the source text.
    """

    metadata: RunMetadata
    extraction: ExtractionOutput
    roles: RoleOutputs
    review: ReviewOutput
    source_map: list[SourceMapEntry] = Field(
        description="Decision ID → source quote mapping. Also written to source-map.json."
    )
