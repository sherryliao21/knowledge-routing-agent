# Knowledge Routing Agent

> Transform messy meeting notes into source-grounded, role-specific reports for software teams.

Built for the [Kaggle AI Agents: Intensive Vibe Coding Capstone](https://www.kaggle.com/competitions/vibecoding-agents-capstone-project), using [Google ADK](https://adk.dev/) and [Antigravity](https://antigravity.dev/).

---

## Problem

Software teams often have long meeting notes, planning discussions, and requirement drafts, but every role receives the same document.

Engineers, QA, PMs, System Analysts, and stakeholders need different context from the same source material. A generic summary is not enough: it can hide uncertainty, bury decisions, and make vague discussion look like confirmed project knowledge.

## Solution

Knowledge Routing Agent turns a Markdown meeting note into:

- structured JSON output
- a source map linking decisions to source quotes
- five role-specific views
- an AI reviewer checklist
- a static HTML report suitable for GitHub Pages

Every extracted item is grounded in source evidence. If a claim is unclear, it is labeled `inferred_needs_confirmation` instead of being presented as confirmed.

## What It Does

```text
Messy Markdown meeting notes
  → source-grounded decision extraction
  → knowledge distillation
  → role-specific context routing
  → AI reviewer plus human review
  → static HTML report (GitHub Pages-ready)
```

Every extracted decision includes the source quote it came from. If no clear source exists, it is labeled `inferred_needs_confirmation` — never presented as a confirmed decision.

## Architecture

```text
SequentialAgent (knowledge_routing_pipeline)
├── decision_extractor     LlmAgent  → extracts sourced decisions
├── ParallelAgent
│   ├── engineer_router    LlmAgent  → engineer view
│   ├── qa_router          LlmAgent  → QA view
│   ├── pm_router          LlmAgent  → PM view
│   ├── sa_router          LlmAgent  → System Analyst view
│   └── stakeholder_router LlmAgent  → stakeholder view
└── reviewer               LlmAgent  → hallucination + quality + safety check
```

The pipeline runs sequentially to extract decisions, route them to parallel role agents, and then review them. The `report_builder` is a pure Python module that executes after the ADK agent pipeline completes, loading the validated structured JSON and rendering the static HTML reports via Jinja2 templates.

## Why Agents

This project uses multiple agents because each stage has a distinct responsibility:

- `decision_extractor` acts like a requirements analyst: it extracts decisions, requirements, risks, dependencies, deadlines, and open questions with source evidence.
- `role_router` runs five role-specific agents in parallel so the same source material becomes different context for different audiences.
- `reviewer` acts as a final quality and safety reviewer, checking role outputs against extracted decisions and flagging unsupported claims, prompt injection attempts, and sensitive content.

This separation keeps the pipeline inspectable: extraction, routing, and review can be evaluated independently.

## Tool Use

- **Google ADK** orchestrates the multi-agent workflow using `SequentialAgent` and `ParallelAgent`.
- **Gemini** powers the extraction, role routing, and reviewer agents.
- **Pydantic** defines structured schemas between agents so outputs are not freeform strings.
- **Jinja2** renders static HTML reports from validated structured output.
- **Click** provides a small CLI for repeatable local runs.
- **GitHub Pages** publishes generated reports as static files without requiring a backend.
- **uv** manages Python dependencies and reproducible setup.

## Role Outputs

From a single meeting notes file, the agent generates five role-specific views:

| Role | Gets |
|---|---|
| **Engineer** | Implementation scope, technical constraints, relevant decisions, open technical questions |
| **QA** | Acceptance criteria, test scenarios, edge cases, unresolved behavior |
| **PM** | Milestones, risks, alignment gaps, open questions, dependencies, decision history |
| **System Analyst** | System requirements, data flows, interface contracts, constraints & architectural decisions, open analysis questions |
| **Stakeholder** | Concise business summary, impact, decisions needing alignment, major unresolved questions |

## Setup

Ensure you have Python 3.11+ installed.

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

Make sure not to commit the `.env` file containing your real API keys.

## Run

```bash
uv run knowledge-route run samples/2026-07-01-planning.md \
  --title "Planning Sync" \
  --date 2026-07-01
```

> [!WARNING]
> By default, the raw meeting notes are omitted from the output report to protect privacy (see [Security](#security)). Pass the `--include-transcript` flag to explicitly opt in to embedding the raw transcript text.

## Outputs

Running the agent generates the following output files:

```text
reports/runs/2026-07-01-planning/
├── index.html      ← role-specific tabbed report
├── output.json     ← structured extracted data
└── source-map.json ← decision → source quote mapping
```

Open the central hub index file at `reports/index.html` to view the full archive of all runs.

## Deployment

The live demo is deployed with GitHub Pages as a static site.

The repository includes `.github/workflows/deploy-pages.yml`, which uploads the `reports/` directory whenever changes are pushed to `main`.

To reproduce deployment:

1. Enable GitHub Pages for the repository.
2. Use the included workflow.
3. Push generated report files under `reports/` to `main`.
4. GitHub Actions deploys the static report archive.

No backend service is required.

## Security

- API keys are loaded from `.env` and never hardcoded in the codebase.
- `.env` is excluded from version control via `.gitignore`.
- `.env.example` contains placeholders only; no API keys or passwords are committed.
- Input validation: only `.md` files are accepted, capped at a maximum size of 50,000 characters.
- **Raw notes are private by default** — `raw_notes` is stored as an empty string in `output.json` and the Transcript tab is hidden in the HTML report.
- Users must explicitly pass the `--include-transcript` flag to opt in to embedding the full source text in public-facing report files.
- Prompt injection defense: the `decision_extractor` agent is instructed to treat the raw meeting notes as untrusted user data, preventing override instructions.
- The `reviewer` agent flags detected prompt injection attempts and sensitive content (such as API keys or credentials) in dedicated warning fields, preventing silent bypasses.

## Evaluation

The repository includes sample inputs and generated reports for several scenarios:

- normal planning notes
- prompt injection test notes
- vague / low-signal notes
- empty file validation
- non-Markdown file validation
- oversized file validation

The test script in `scripts/run_tests.sh` checks that the pipeline can run, generated outputs are created, prompt-injection warning fields exist, and invalid inputs are rejected.

## Tech Stack

- [Google ADK](https://adk.dev/) — multi-agent pipeline orchestration (SequentialAgent + ParallelAgent)
- [Gemini](https://ai.google.dev/) — LLM for all extraction, routing, and review steps
- [Pydantic](https://docs.pydantic.dev/) — structured output schemas
- [Jinja2](https://jinja.palletsprojects.com/) — HTML report rendering
- [Click](https://click.palletsprojects.com/) — CLI implementation
- [uv](https://docs.astral.sh/uv/) — package management
- [Antigravity](https://antigravity.dev/) — AI coding assistant

## License

MIT
