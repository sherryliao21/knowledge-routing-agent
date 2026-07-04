# Walkthrough: Knowledge Routing Agent v1.3

We have successfully built, verified, and published **v1.3** to the `main` branch. 

---

## 🌟 Codebase Summary

### 📂 File Structure
```
capstone/
├── .env.example          ← Template for API keys
├── .gitignore            ← Excludes local secrets (.env)
├── README.md             ← Main project documentation with security/flag usage
├── pyproject.toml        ← Dependencies and CLI entrypoints
├── uv.lock               ← Locked dependency matrix
├── src/
│   ├── agent.py          ← SequentialAgent core pipeline
│   ├── cli/
│   │   └── main.py       ← CLI Entrypoint (run command + validations + --include-transcript flag)
│   ├── core/
│   │   ├── parser.py     ← Input parser and security guards
│   │   ├── decision_extractor.py ← Decision extraction agent (injection defense)
│   │   ├── role_router.py   ← Parallel routing agent (5 roles: Engineer, QA, PM, SA, Stakeholder)
│   │   ├── reviewer.py       ← Hallucination + Quality + Injection check agent
│   │   └── report_builder.py ← Renders HTML and Hub page
│   ├── prompts/          ← Markdown prompts (with ownership rules applied)
│   │   ├── decision_extractor.md
│   │   ├── engineer_router.md
│   │   ├── pm_router.md
│   │   ├── sa_router.md   
│   │   ├── qa_router.md
│   │   └── reviewer.md
│   ├── schemas/
│   │   └── models.py     ← Pydantic schemas (added CitedItem, split constraints/decisions)
│   └── templates/        ← HTML dashboard templates (Soft Structuralism light mode)
├── samples/
│   ├── 2026-07-01-planning.md       ← Phoenix kickoff sample notes
│   ├── 2026-07-02-injection-test.md ← Injection test notes
│   └── 2026-07-03-vague-notes.md     ← Vague requirements notes
├── scripts/
│   └── run_tests.sh      ← Automated test suite runner (T2/T3/T4)
└── reports/              ← Git-tracked reports directory for GH Pages
    ├── index.html        ← The central knowledge Hub (Soft Structuralism redesign)
    ├── assets/           ← Stakeholder photos and emblem assets
    └── runs/
        └── 2026-07-01-project-phoenix-kickoff/
            ├── index.html       ← Interactive tabbed report (3-state badge, split constraints)
            ├── output.json      ← Serialized structured data (with CitedItem structures)
            └── source-map.json  ← Decision ID -> quote mappings
```

---

## 🔒 Implemented Security & Privacy Hardening

1. **Opt-in Transcript Isolation:** By default, the raw meeting notes are **never** written to the generated reports directory to prevent accidental leakage of sensitive conversations. To publish the transcript tab in the HTML report, users must explicitly supply the `--include-transcript` flag.
2. **Prompt Injection Defenses:** The `decision_extractor` prompt treats incoming notes as untrusted data rather than instructions. If a user inserts instructions trying to bypass confirmation/grounding, they are ignored.
3. **Automated Warning Flags:** The `reviewer` agent checks for injection patterns and sensitive information (credentials, PII). Flagged warning strings are stored in `prompt_injection_warnings` and `sensitive_content_warnings` fields and displayed as highlighted banners in the dashboard header.

---

## 📊 v1.3 Refinements

### 1. Three-State Reviewer Badge
- Replace the binary PASS/FLAG status indicator with a 3-state badge:
  - **Clean Pass (Green):** Approved with zero issues flagged.
  - **Approved with Notes (Amber):** Approved with non-blocking warning-level notes from the reviewer.
  - **Flag Needed (Red):** Critical issues require human intervention.
- Added a standard Remix info icon (`ri-information-line`) with a hover tooltip clarifying the Reviewer is an automated AI agent.

### 2. Constraints vs. Architectural Decisions Split
- Created a `CitedItem` type in `models.py` associating items with relevant decision IDs.
- Separated **Constraints** (external limitations like deadlines, budget, performance targets) from **Architectural Decisions** (technology stacks chosen by the team).
- Rendered these split lists with inline decision pill tags in both the Engineer and System Analyst panels.

### 3. Open Question Ownership Routing
- Integrated ownership rules in all role router prompts to prevent broadcasting the same open questions verbatim. Gaps are assigned to specific roles responsible for resolving them (e.g. registration acceptance criteria gaps go to PM/QA; session token/API timing details go to Engineer/SA).

### 4. PM Panel Reordering & Collapse
- Rearranged the Project Manager panel to display actionable items (Milestones, Risks, Gaps, Open Questions, Dependencies) first.
- Collapsed the long "Decision History" under a native `<details>` accordion by default to reduce daily cognitive load.

---

## 🚀 Live Test Verification

All automated tests passed successfully:
```
==================================================
  Knowledge Route Agent — Test Suite
==================================================
✓ PASS — T2: Pipeline completed successfully
✓ PASS — T2: output.json created
✓ PASS — T2: prompt_injection_warnings field exists in output.json
✓ PASS — T3: Pipeline completed successfully
✓ PASS — T3: output.json created
✓ PASS — T4: Empty file correctly rejected by parser
✓ PASS — T4b: Non-markdown file correctly rejected
✓ PASS — T4c: Oversized file correctly rejected
==================================================
```
