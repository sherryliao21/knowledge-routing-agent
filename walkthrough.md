# Walkthrough: Knowledge Routing Agent v1.1

We have successfully built, verified, and published **v1.1** to the `main` branch. 

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
│   ├── prompts/          ← Markdown prompts (with pm_router and sa_router split)
│   │   ├── decision_extractor.md
│   │   ├── engineer_router.md
│   │   ├── pm_router.md
│   │   ├── sa_router.md   ← [NEW] System Analyst prompt focusing on system design
│   │   ├── qa_router.md
│   │   └── reviewer.md
│   ├── schemas/
│   │   └── models.py     ← Pydantic schemas (added SAView, milestones, injection warning fields)
│   └── templates/        ← HTML dashboard templates (Soft Structuralism light mode)
├── samples/
│   ├── 2026-07-01-planning.md       ← Phoenix kickoff sample notes
│   ├── 2026-07-02-injection-test.md ← [NEW] Injection test notes
│   └── 2026-07-03-vague-notes.md     ← [NEW] Vague requirements notes
├── scripts/
│   └── run_tests.sh      ← [NEW] Automated test suite runner (T2/T3/T4)
└── reports/              ← Git-tracked reports directory for GH Pages
    ├── index.html        ← The central knowledge Hub (Soft Structuralism redesign)
    ├── assets/           ← Stakeholder photos and emblem assets
    └── runs/
        └── 2026-07-01-project-phoenix-kickoff/
            ├── index.html       ← Interactive tabbed report
            ├── output.json      ← Serialized structured data (privacy-safe by default)
            └── source-map.json  ← Decision ID -> quote mappings
```

---

## 🔒 Implemented Security & Privacy Hardening (v1.1)

1. **Opt-in Transcript Isolation:** By default, the raw meeting notes are **never** written to the generated reports directory to prevent accidental leakage of sensitive conversations. To publish the transcript tab in the HTML report, users must explicitly supply the `--include-transcript` flag.
2. **Prompt Injection Defenses:** The `decision_extractor` prompt treats incoming notes as untrusted data rather than instructions. If a user inserts instructions trying to bypass confirmation/grounding, they are ignored.
3. **Automated Warning Flags:** The `reviewer` agent checks for injection patterns and sensitive information (credentials, PII). Flagged warning strings are stored in `prompt_injection_warnings` and `sensitive_content_warnings` fields and displayed as highlighted banners in the dashboard header.

---

## 📊 Split of PM (Project Manager) & SA (System Analyst) Roles

Previously combined, we separated them into two distinct operational contexts:
- **Project Manager (Sarah):** Focuses strictly on delivery timeline, cross-team dependencies, project risks, alignment gaps, and delivery milestones.
- **System Analyst (Alex):** Focuses strictly on architectural system design, writing formal specifications ("SHALL/MUST NOT" requirements), data flows/integrations, and interface/API contracts.

---

## 🎨 Premium Light Mode (Soft Structuralism Vibe)

Following the **High-End UI/UX design** guidelines:
- **Palette:** Crisp Slate & Off-White (`#f5f5f5` / `#ffffff`) base theme with distinct color accents per role card.
- **Navigation Row:** Horizontal navigation row displaying cards for the five roles plus decisions log, each complete with custom profile pictures (Dave, John, Emma, Sarah, Alex) and colored glowing rings.
- **Responsive:** Fits nicely on 375px mobile screens with smooth horizontal scroll-snap buttons.

---

## 🚀 Live Test Verification

We wrote an automated test runner `capstone/scripts/run_tests.sh` that validates:
- **T2 (Injection Detection):** Confirms that prompt injection warnings are caught and populated.
- **T3 (Vague Requirements):** Validates processing notes with incomplete details.
- **T4 (Boundary Checks):** Verifies correct rejection of empty files, plain-text formats, and oversized uploads.

All tests passed successfully:
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
