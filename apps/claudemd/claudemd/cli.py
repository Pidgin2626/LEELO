"""CLI entry: `claudemd init`, `claudemd audit`."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from . import __version__
from .generator import audit as audit_md
from .generator import generate
from .interview import run_interview
from .scanner import scan


def _check_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        click.secho(
            "ANTHROPIC_API_KEY is not set. On Windows PowerShell:\n"
            '  $env:ANTHROPIC_API_KEY = "sk-ant-..."',
            fg="red",
        )
        sys.exit(1)


@click.group()
@click.version_option(__version__)
def main() -> None:
    """Generate and audit CLAUDE.md files for any project."""


@main.command()
@click.option(
    "--path",
    "target",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path.cwd(),
    show_default="current directory",
    help="Project directory to analyze.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite an existing CLAUDE.md without asking.",
)
@click.option(
    "--no-interview",
    is_flag=True,
    help="Skip the interactive questions and let Claude infer everything.",
)
def init(target: Path, force: bool, no_interview: bool) -> None:
    """Create a CLAUDE.md in the target directory."""
    _check_api_key()
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    out_path = target / "CLAUDE.md"

    if out_path.exists() and not force:
        if not click.confirm(
            f"CLAUDE.md already exists at {out_path}. Overwrite?", default=False
        ):
            click.echo("Aborted. Use --force to skip this prompt.")
            sys.exit(0)

    click.secho(f"Scanning {target} ...", fg="cyan")
    scan_result = scan(target)

    if scan_result["is_empty"]:
        click.secho(
            "  (directory looks empty — that's fine, the interview will fill the gaps)",
            fg="yellow",
        )
    else:
        click.echo(
            f"  found {scan_result['total_files_scanned']} files, "
            f"{len(scan_result['languages'])} languages, "
            f"{len(scan_result['found_files'])} config files"
        )

    answers: dict = {}
    if not no_interview:
        answers = run_interview()

    click.secho("\nGenerating CLAUDE.md ...\n", fg="cyan")
    md = generate(scan_result, answers)

    out_path.write_text(md + "\n", encoding="utf-8")
    click.secho(f"\nWrote {out_path}", fg="green")


@main.command()
@click.option(
    "--path",
    "target",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path.cwd(),
    show_default="current directory",
    help="Project directory to audit.",
)
def audit(target: Path) -> None:
    """Review an existing CLAUDE.md and suggest improvements."""
    _check_api_key()
    target = target.resolve()
    md_path = target / "CLAUDE.md"
    if not md_path.exists():
        click.secho(
            f"No CLAUDE.md found at {md_path}. Run `claudemd init` first.",
            fg="red",
        )
        sys.exit(1)

    existing = md_path.read_text(encoding="utf-8")
    click.secho(f"Auditing {md_path} ...\n", fg="cyan")
    scan_result = scan(target)
    audit_md(existing, scan_result)
    click.echo("")


if __name__ == "__main__":
    main()
