"""
Report Builder.

Renders and writes all output artifacts for a pipeline run:
  - reports/runs/<run_id>/output.json      (full structured views/metadata)
  - reports/runs/<run_id>/source-map.json  (decision ID -> quote mappings)
  - reports/runs/<run_id>/index.html       (tabbed, interactive HTML brief)
  - reports/index.html                     (global Hub page listing all runs)

SECURITY RULE ENFORCED STRUCTURALLY:
Raw meeting notes text is NEVER written to any output file.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from src.schemas.models import RunOutput

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"


def build_run_artifacts(run_data: RunOutput) -> Path:
    """
    Generate all files for a single run and rebuild the central Hub.

    Args:
        run_data: Complete output of the agent pipeline.

    Returns:
        The Path to the generated run HTML file.
    """
    run_id = run_data.metadata.run_id
    run_dir = _REPORTS_DIR / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # 1. Write structured JSON files (Security: raw notes NOT inside run_data)
    # -----------------------------------------------------------------------
    output_json_path = run_dir / "output.json"
    output_json_path.write_text(
        run_data.model_dump_json(indent=2),
        encoding="utf-8"
    )

    source_map_json_path = run_dir / "source-map.json"
    source_map_entries = [entry.model_dump() for entry in run_data.source_map]
    source_map_json_path.write_text(
        json.dumps(source_map_entries, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # -----------------------------------------------------------------------
    # 2. Render Run Report HTML
    # -----------------------------------------------------------------------
    jinja_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)))
    report_template = jinja_env.get_template("report.html")

    # Jinja expects dicts/standard values for rendering
    data_dict = run_data.model_dump()
    
    html_content = report_template.render(**data_dict)
    
    report_html_path = run_dir / "index.html"
    report_html_path.write_text(html_content, encoding="utf-8")

    # -----------------------------------------------------------------------
    # 3. Rebuild Central Hub (reports/index.html)
    # -----------------------------------------------------------------------
    rebuild_hub()

    return report_html_path


def rebuild_hub() -> Path:
    """
    Scan all runs and regenerate the central reports/index.html Hub page.
    """
    runs_data = []
    runs_dir = _REPORTS_DIR / "runs"

    if runs_dir.exists():
        # Scan subdirectories containing output.json
        for path in sorted(runs_dir.iterdir(), reverse=True):
            if path.is_dir() and (path / "output.json").exists():
                try:
                    raw_data = json.loads((path / "output.json").read_text(encoding="utf-8"))
                    
                    # Extract fields needed for the Hub cards
                    metadata = raw_data.get("metadata", {})
                    roles = raw_data.get("roles", {})
                    review = raw_data.get("review", {})
                    extraction = raw_data.get("extraction", {})
                    
                    # Use stakeholder summary or plain overview
                    summary = roles.get("stakeholder", {}).get("business_summary", "")
                    
                    runs_data.append({
                        "run_id": metadata.get("run_id"),
                        "title": metadata.get("title", "Untitled Run"),
                        "date": metadata.get("date", "Unknown Date"),
                        "summary": summary,
                        "decisions_count": len(extraction.get("decisions", [])),
                        "review_status": review.get("status", "PASS"),
                    })
                except Exception as e:
                    # Skip corrupt runs so the dashboard doesn't crash
                    print(f"⚠️ Warning: skipping corrupt report run directory at {path.name}: {e}")

    # Render central Hub index
    jinja_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)))
    index_template = jinja_env.get_template("index.html")
    hub_content = index_template.render(runs=runs_data)

    hub_html_path = _REPORTS_DIR / "index.html"
    hub_html_path.write_text(hub_content, encoding="utf-8")

    return hub_html_path
