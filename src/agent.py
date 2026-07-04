"""
Knowledge Routing Agent — root pipeline.

Wires all stages into a SequentialAgent:

  decision_extractor
      ↓
  role_router (ParallelAgent: engineer + QA + PM + stakeholder)
      ↓
  reviewer

After this pipeline completes, the CLI calls report_builder to generate
the static HTML + JSON output files.
"""

from google.adk.agents import SequentialAgent

from src.core.decision_extractor import decision_extractor
from src.core.role_router import role_router
from src.core.reviewer import reviewer

root_agent = SequentialAgent(
    name="knowledge_routing_pipeline",
    description=(
        "Transforms messy meeting notes into source-grounded, role-specific "
        "knowledge artifacts. Runs extraction → role routing → review in sequence."
    ),
    sub_agents=[
        decision_extractor,
        role_router,
        reviewer,
    ],
)
