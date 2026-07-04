"""
CLI Entrypoint for the Knowledge Routing Agent.

Handles:
  1. CLI arguments (--title, --date)
  2. Input security validation (file type and size cap)
  3. ADK Pipeline execution (Extraction → Routing → Review)
  4. Pydantic mapping & structured persistence
  5. HTML Report & Hub compilation
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv

# Bridge GOOGLE_API_KEY to GEMINI_API_KEY dynamically
load_dotenv()
if "GOOGLE_API_KEY" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from src.agent import root_agent
from src.core.parser import parse_meeting_notes, ParserError
from src.core.report_builder import build_run_artifacts
from src.schemas.models import (
    RunOutput,
    RunMetadata,
    ExtractionOutput,
    RoleOutputs,
    EngineerView,
    QAView,
    PMView,
    StakeholderView,
    ReviewOutput,
    SourceMapEntry,
)


async def _execute_pipeline(
    raw_text: str,
    app_name: str,
    user_id: str,
    session_id: str,
) -> tuple[dict, dict, dict, dict, dict, dict]:
    """Execute the ADK sequential + parallel pipeline on the asyncio loop."""
    runner = InMemoryRunner(agent=root_agent, app_name=app_name)

    # 1. Create the stateful session explicitly
    runner.session_service.create_session_sync(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={"raw_notes": raw_text},
    )

    # 2. Run the pipeline async generator
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=Content(parts=[Part(text="Analyse meeting notes")]),
    ):
        # We can print clean stage logs in the CLI as they complete
        if event.node_name:
            click.echo(f"  [Agent] Completed stage: {event.node_name}...")

    # 3. Retrieve the final state
    session = runner.session_service.get_session_sync(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )
    if not session:
        raise RuntimeError("Agent session disappeared after completion.")

    return (
        session.state.get("extraction"),
        session.state.get("engineer_view"),
        session.state.get("qa_view"),
        session.state.get("pm_view"),
        session.state.get("stakeholder_view"),
        session.state.get("review"),
    )


@click.group()
def cli():
    """Knowledge Routing Agent CLI.

    Transforms unstructured project discussions into source-grounded,
    role-specific developer plans.
    """
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--title",
    "-t",
    help="Human-readable title for the report (defaults to filename).",
)
@click.option(
    "--date",
    "-d",
    help="Meeting date in YYYY-MM-DD format (defaults to today).",
)
@click.option(
    "--include-transcript",
    is_flag=True,
    default=False,
    help="Publish the full raw notes in the report HTML. OFF by default for privacy.",
)
def run(file_path: str, title: str | None, date: str | None, include_transcript: bool):
    """Compile unstructured meeting notes into structured role views."""
    # Check for API key before starting
    if not os.environ.get("GEMINI_API_KEY"):
        click.secho(
            "Error: GOOGLE_API_KEY or GEMINI_API_KEY not found in environment.\n"
            "Please copy .env.example to .env and fill in your Gemini API key.",
            fg="red",
            bold=True,
            err=True,
        )
        sys.exit(1)

    # Defaults
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            click.secho(
                f"Error: Invalid date format '{date}'. Must be YYYY-MM-DD.",
                fg="red",
                bold=True,
                err=True,
            )
            sys.exit(1)

    path = Path(file_path)
    if not title:
        title = path.stem.replace("-", " ").replace("_", " ").title()

    # Step 1: Parse and validate input (Security checks)
    click.echo(f"[*] Parsing and validating input file: {path.name}...")
    try:
        parsed_doc = parse_meeting_notes(file_path, title, date)
    except ParserError as e:
        click.secho(f"Security/Format Validation Error: {e}", fg="red", bold=True, err=True)
        sys.exit(1)

    click.echo(f"  - Size: {parsed_doc.char_count:,} characters")
    click.echo(f"  - Run ID: {parsed_doc.run_id}")

    # Step 2: Execute Multi-Agent Pipeline
    click.echo("[*] Initialising Multi-Agent pipeline (gemini-2.5-flash)...")
    app_name = "knowledge-routing-agent"
    user_id = "cli-user"
    session_id = f"run-{parsed_doc.run_id}"

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        res = loop.run_until_complete(
            _execute_pipeline(parsed_doc.raw_text, app_name, user_id, session_id)
        )
    except Exception as e:
        click.secho(f"Pipeline Error: {e}", fg="red", bold=True, err=True)
        sys.exit(1)

    ext_data, eng_data, qa_data, pm_data, stak_data, rev_data = res

    # Check that we received all values
    if not all([ext_data, eng_data, qa_data, pm_data, stak_data, rev_data]):
        click.secho(
            "Error: Pipeline completed but some role views were missing in output.",
            fg="red",
            bold=True,
            err=True,
        )
        sys.exit(1)

    # Step 3: Map to Pydantic models
    click.echo("[*] Mapping and validating final schemas...")
    
    # Session state values might be dicts or Pydantic instances depending on runner wrapper
    def to_model(data, model_cls):
        if isinstance(data, model_cls):
            return data
        return model_cls.model_validate(data)

    try:
        extraction = to_model(ext_data, ExtractionOutput)
        engineer = to_model(eng_data, EngineerView)
        qa = to_model(qa_data, QAView)
        pm = to_model(pm_data, PMView)
        stakeholder = to_model(stak_data, StakeholderView)
        review = to_model(rev_data, ReviewOutput)
    except Exception as e:
        click.secho(f"Schema Validation Error: {e}", fg="red", bold=True, err=True)
        sys.exit(1)

    # Build metadata block
    metadata = RunMetadata(
        title=parsed_doc.title,
        date=parsed_doc.date,
        run_id=parsed_doc.run_id,
        source_file=parsed_doc.source_filename,
        generated_at=datetime.utcnow().isoformat() + "Z",
    )

    # Build source map entries (Decision ID -> Quote list)
    source_map = []
    for d in extraction.decisions:
        quotes = [ev.quote for ev in d.evidence]
        source_map.append(
            SourceMapEntry(
                decision_id=d.id,
                decision_title=d.title,
                confidence=d.confidence,
                evidence_quotes=quotes,
            )
        )

    # Bundle into root RunOutput
    # raw_notes is opt-in only: requires --include-transcript flag
    if include_transcript:
        click.secho(
            "[!] Warning: --include-transcript is active. The full raw notes will be "
            "written to output.json and the report HTML. Only use with synthetic or "
            "sanitized notes.",
            fg="yellow",
            bold=True,
        )
        raw_notes_value = parsed_doc.raw_text
    else:
        raw_notes_value = ""

    run_output = RunOutput(
        metadata=metadata,
        extraction=extraction,
        roles=RoleOutputs(
            engineer=engineer,
            qa=qa,
            pm=pm,
            stakeholder=stakeholder,
        ),
        review=review,
        source_map=source_map,
        raw_notes=raw_notes_value,
    )

    # Step 4: Write artifacts and build Hub
    click.echo("[*] Writing static report artifacts...")
    try:
        report_html_path = build_run_artifacts(run_output)
    except Exception as e:
        click.secho(f"Report Generation Error: {e}", fg="red", bold=True, err=True)
        sys.exit(1)

    # Print success summaries
    click.secho("\n🎉 Run completed successfully!", fg="green", bold=True)
    click.echo(f"  - Extracted Decisions: {extraction.total_confirmed} confirmed, {extraction.total_inferred} inferred")
    
    if review.status == "PASS":
        click.secho("  - Verification Status: PASS (Approved)", fg="green")
    else:
        click.secho(
            f"  - Verification Status: FLAG NEEDED ({len(review.issues)} issues flagged)",
            fg="yellow",
            bold=True,
        )
        for issue in review.issues:
            click.echo(f"    [{issue.severity.upper()}] {issue.location}: {issue.description}")

    click.echo(f"\nWritten to: {report_html_path.relative_to(Path.cwd().parent)}")
    click.echo(f"Hub index:  {Path(report_html_path.parent.parent.parent / 'index.html').relative_to(Path.cwd().parent)}")


if __name__ == "__main__":
    cli()
