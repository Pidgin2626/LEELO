"""CLI: `council ask`, `council log`, `council show`, `council panel`."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from . import __version__
from .orchestrator import render_full, run_council
from .providers import default_panel, solo_claude_panel
from .storage import get as get_decision
from .storage import list_decisions, save


def _resolve_panel(solo: bool) -> list:
    if solo:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            click.secho(
                "Solo mode needs ANTHROPIC_API_KEY. Set it and retry.",
                fg="red",
            )
            sys.exit(1)
        return solo_claude_panel()

    panel = default_panel()
    if not panel:
        click.secho(
            "No advisor API keys found. Set at least ANTHROPIC_API_KEY "
            "(and optionally OPENAI_API_KEY, GOOGLE_API_KEY, XAI_API_KEY, "
            "DEEPSEEK_API_KEY) and retry. Or pass --solo for an all-Claude panel.",
            fg="red",
        )
        sys.exit(1)
    return panel


@click.group()
@click.version_option(__version__)
def main() -> None:
    """A panel of LLMs debates your hard question and gives you a verdict."""


@main.command()
@click.argument("question", required=False)
@click.option(
    "--file",
    "question_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Read the question from a file instead of the command line.",
)
@click.option(
    "--solo",
    is_flag=True,
    help="Use 5 Claude advisors with different personas (no other API keys needed).",
)
@click.option(
    "--out",
    "out_path",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Save the full markdown verdict + transcript to this file.",
)
def ask(
    question: str | None,
    question_file: Path | None,
    solo: bool,
    out_path: Path | None,
) -> None:
    """Run the panel on QUESTION (or from --file)."""
    if question_file:
        question = question_file.read_text(encoding="utf-8").strip()
    if not question:
        click.secho("Provide a question, or --file PATH.", fg="red")
        sys.exit(1)

    panel = _resolve_panel(solo)
    click.echo(f"Panel: {', '.join(a.name for a in panel)}\n")

    result = run_council(question, panel)

    full = render_full(result)
    click.echo("\n" + "=" * 60)
    click.secho("FINAL VERDICT", fg="green", bold=True)
    click.echo("=" * 60 + "\n")
    click.echo(result.synthesis)

    decision_id = save(result)
    click.secho(f"\n[saved as decision #{decision_id}]", fg="cyan")

    if out_path:
        out_path.write_text(full, encoding="utf-8")
        click.secho(f"[wrote full transcript to {out_path}]", fg="cyan")


@main.command(name="log")
@click.option(
    "--limit",
    type=int,
    default=25,
    help="How many recent decisions to list.",
)
def list_cmd(limit: int) -> None:
    """List previous council decisions."""
    rows = list_decisions(limit=limit)
    if not rows:
        click.echo("No decisions logged yet.")
        return
    for r in rows:
        q = r["question"].replace("\n", " ")
        if len(q) > 90:
            q = q[:87] + "..."
        click.echo(f"#{r['id']:>3}  {r['created_at'][:19]}  {q}")


@main.command()
@click.argument("decision_id", type=int)
@click.option(
    "--full",
    is_flag=True,
    help="Show the full transcript (default: just the verdict).",
)
def show(decision_id: int, full: bool) -> None:
    """Show a saved decision by its number."""
    row = get_decision(decision_id)
    if not row:
        click.secho(f"No decision #{decision_id}.", fg="red")
        sys.exit(1)

    click.echo(f"# Decision #{row['id']}  ({row['created_at'][:19]})\n")
    click.echo(f"## Question\n\n{row['question']}\n")
    click.echo(f"## Panel\n")
    for a in row["advisors"]:
        click.echo(f"- {a['name']} ({a['model_id']}) — {a['persona']}")
    click.echo(f"\n## Synthesis\n\n{row['synthesis']}\n")
    if full:
        click.echo("---\n")
        click.echo(row["transcript_md"])


@main.command()
def panel() -> None:
    """Show which advisors are available given your current API keys."""
    keys = {
        "ANTHROPIC_API_KEY": "Claude",
        "OPENAI_API_KEY": "GPT",
        "GOOGLE_API_KEY": "Gemini",
        "XAI_API_KEY": "Grok",
        "DEEPSEEK_API_KEY": "DeepSeek",
    }
    click.echo("Advisor availability:\n")
    for env, name in keys.items():
        marker = click.style("yes", fg="green") if os.environ.get(env) else click.style("no", fg="red")
        click.echo(f"  {name:<10} ({env:<22}): {marker}")
    available = [n for env, n in keys.items() if os.environ.get(env)]
    click.echo(
        f"\nWill run a panel of {len(available)} advisor(s): {', '.join(available) or 'none'}"
    )
    if len(available) < 2:
        click.echo("\nTip: pass --solo to run 5 Claude advisors with different personas.")


if __name__ == "__main__":
    main()
