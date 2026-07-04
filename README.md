# Knowledge Routing Agent

> Transform messy meeting notes into source-grounded, role-specific knowledge artifacts.

Built for the [Kaggle AI Agents: Intensive Vibe Coding Capstone](https://www.kaggle.com/competitions/vibecoding-agents-capstone-project), using [Google ADK](https://adk.dev/) and [Antigravity](https://antigravity.dev/).

---

## What It Does

```
Messy Markdown meeting notes
  → source-grounded decision extraction
  → knowledge distillation
  → role-specific context routing
  → human review checklist
  → static HTML report (GitHub Pages-ready)
```

Every extracted decision includes the source quote it came from. If no clear source exists, it is labeled `inferred_needs_confirmation` — never presented as a confirmed decision.

## Role Outputs

From a single meeting notes file, the agent generates four role-specific views:

| Role | Gets |
|---|---|
| **Engineer** | Implementation scope, technical constraints, relevant decisions, open technical questions |
| **QA** | Acceptance criteria, test scenarios, edge cases, unresolved behavior |
| **PM / SA** | Decision history, dependencies, risks, alignment gaps, open questions |
| **Stakeholder** | Concise business summary, impact, decisions needing alignment, major unresolved questions |

## Architecture

```
SequentialAgent (knowledge_routing_pipeline)
├── decision_extractor     LlmAgent  → extracts sourced decisions
├── ParallelAgent
│   ├── engineer_router    LlmAgent  → engineer view
│   ├── qa_router          LlmAgent  → QA view
│   ├── pm_router          LlmAgent  → PM/SA view
│   └── stakeholder_router LlmAgent  → stakeholder view
└── reviewer               LlmAgent  → quality + hallucination check
   (report_builder runs after pipeline — pure Python, Jinja2)
```

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Run

```bash
uv run knowledge-route run samples/2026-07-01-planning.md \
  --title "Planning Sync" \
  --date 2026-07-01

# Optionally embed the raw notes in the report (off by default — see Security)
uv run knowledge-route run samples/my-notes.md --title "My Meeting" --include-transcript
```

Output files:

```
reports/runs/2026-07-01-planning/
├── index.html      ← role-specific tabbed report
├── output.json     ← structured extracted data
└── source-map.json ← decision → source quote mapping
```

Open `reports/index.html` for the full archive of all runs.

## Security

- API keys are loaded from `.env` and never hardcoded
- `.env` is excluded from git via `.gitignore`
- Input is validated: only `.md` files accepted, capped at 50,000 characters
- **Raw notes are private by default** — `raw_notes` is an empty string in `output.json` and the Transcript tab is hidden in the HTML report
- Pass `--include-transcript` to opt in to embedding the full source text (only use with synthetic or pre-sanitised notes, since they will be written to a public-deployable file)
- Prompt injection defense: the extractor is instructed to treat meeting notes as untrusted data; the reviewer flags detected injection attempts and sensitive content in dedicated warning fields

## Tech Stack

- [Google ADK](https://adk.dev/) — multi-agent pipeline (SequentialAgent + ParallelAgent)
- [Gemini](https://ai.google.dev/) — LLM for all extraction and routing
- [Pydantic](https://docs.pydantic.dev/) — structured output schemas
- [Jinja2](https://jinja.palletsprojects.com/) — HTML report templating
- [Click](https://click.palletsprojects.com/) — CLI
- [uv](https://docs.astral.sh/uv/) — package management
- [Antigravity](https://antigravity.dev/) — AI coding assistant

## License

MIT
