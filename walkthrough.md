# Walkthrough: Knowledge Routing Agent MVP v1.0

We have successfully built, verified, and published the **Knowledge Routing Agent MVP v1.0** to the `main` branch. 

---

## 🌟 Codebase Summary

### 📂 File Structure
```
capstone/
├── .env.example          ← Template for API keys
├── .gitignore            ← Excludes local secrets (.env)
├── README.md             ← Main project documentation
├── pyproject.toml        ← Dependencies (google-adk, click, pydantic, jinja2)
├── uv.lock               ← Locked dependency matrix
├── src/
│   ├── agent.py          ← SequentialAgent core pipeline
│   ├── cli/
│   │   └── main.py       ← CLI Entrypoint (run command + validations)
│   ├── core/
│   │   ├── parser.py     ← Input parser and security guards
│   │   ├── decision_extractor.py ← Decision extraction agent
│   │   ├── role_router.py   ← Parallel routing agent (4 roles)
│   │   ├── reviewer.py       ← Hallucination and quality checks agent
│   │   └── report_builder.py ← Renders HTML and Hub page
│   ├── prompts/          ← Markdown templates for the agents
│   ├── schemas/
│   │   └── models.py     ← Pydantic schemas enforcing output types
│   └── templates/        ← HTML dashboards templates (Ethereal Glass style)
├── samples/
│   └── 2026-07-01-planning.md  ← Messy project kickoff sync sample
└── reports/              ← Git-tracked reports directory for GH Pages
    ├── index.html        ← The central knowledge Hub listing all runs
    └── runs/
        └── 2026-07-01-project-phoenix-kickoff/
            ├── index.html       ← Interactive tabbed report
            ├── output.json      ← Serialized structured data (privacy-safe)
            └── source-map.json  ← Decision ID -> quote mappings
```

---

## 🔒 Implemented Security Features (Kaggle Grade)

1. **Strict File Checks:** Input is restricted to `.md` files to prevent malicious scripts from execution.
2. **Size Guardrails:** Capped raw text inputs to `50,000 characters` (~10 pages) to block buffer inflation or massive token bill spikes.
3. **API Keys Isolation:** Excluded `.env` keys from source control using local variables.
4. **Structural Privacy Enforcer:** The raw meeting notes text is processed **entirely in-memory** and **never** written to `output.json`, `source-map.json`, or the HTML templates. Only extracted, verified facts and verbatim citation snippets are persisted, protecting sensitive discussions.

---

## 🎨 Premium Visual System (Ethereal Glass Vibe)

Following the **High-End UI/UX design** patterns:
- **Vibe:** Deep OLED black backgrounds (`#050505`) with custom glowing radial mesh gradients.
- **Components:** Glassmorphic card layouts (`backdrop-filter`) with 1px light borders (`rgba(255,255,255,0.08)`) and soft highlights.
- **Typography:** `Plus Jakarta Sans` for titles/UI, paired with `Geist Mono` for IDs and metadata.
- **Interactions:** Fully interactive tabs to navigate role views, custom collapsible citation accordions, search indexing for decisions, and a clean verification modal window displaying reviewer flags.

---

## 🚀 Live Demonstration Results

Running the kickoff sync of `Project Phoenix`:
```bash
uv run knowledge-route run samples/2026-07-01-planning.md --title "Project Phoenix Kickoff" --date 2026-07-01
```

1. **Parser Gate:** Validated `3,053 characters` of raw discussion notes.
2. **Extraction Stage:** `decision_extractor` extracted **28 confirmed architectural choices and milestones**.
3. **Role Routing:** Routed specifications in parallel to **Engineer**, **QA**, **PM/SA**, and **Stakeholder** contexts.
4. **Reviewer verification:** Executed a hallucination check. Returned **PASS (Approved)** for the kickoff sample.
5. **Report Compilation:** Wrote the structured schema models and the static HTML brief. Updated the Hub Index.

---

## 📈 Next Steps

- **YouTube Video:** Record a 5-minute video demonstrating:
  1. The CLI running on the kickoff markdown file.
  2. The generated premium HTML pages in your browser.
  3. A quick walk-through of `agent.py` and `models.py`.
- **Kaggle Writeup:** You can copy details from `README.md` and this walkthrough for your Kaggle competition report.
