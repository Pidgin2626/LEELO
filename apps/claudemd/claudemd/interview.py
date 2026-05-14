"""Beginner-friendly question flow.

Each question has a sensible default. The user can hit Enter to skip.
We collect freeform answers and pass them to Claude as context for the
CLAUDE.md generator.
"""

from __future__ import annotations

import click


QUESTIONS: list[dict] = [
    {
        "key": "what_is_it",
        "prompt": (
            "1) What are you building, in one sentence?\n"
            "   (e.g. 'a Shopify app that recovers abandoned carts', "
            "or 'just a folder for notes')"
        ),
        "default": "",
    },
    {
        "key": "skill_level",
        "prompt": (
            "2) How experienced are you with this kind of code?\n"
            "   Pick one: beginner / intermediate / advanced"
        ),
        "default": "beginner",
    },
    {
        "key": "tone",
        "prompt": (
            "3) How should Claude talk to you?\n"
            "   (e.g. 'explain things simply, no jargon', "
            "'be terse and skip pleasantries', 'always show me examples')"
        ),
        "default": "explain things simply and show concrete examples",
    },
    {
        "key": "stack_preferences",
        "prompt": (
            "4) Any libraries/tools you LOVE or HATE?\n"
            "   (e.g. 'prefer tailwind over plain CSS', "
            "'no class components in React', 'use pytest not unittest')"
        ),
        "default": "",
    },
    {
        "key": "do_not",
        "prompt": (
            "5) Anything Claude should NEVER do?\n"
            "   (e.g. 'never push to main', 'never run rm', "
            "'never install new dependencies without asking')"
        ),
        "default": "",
    },
    {
        "key": "run_commands",
        "prompt": (
            "6) How do you run / test / build this project?\n"
            "   (e.g. 'npm run dev to start, npm test to test'). "
            "Hit Enter to let Claude guess from the files."
        ),
        "default": "",
    },
    {
        "key": "extra",
        "prompt": (
            "7) Anything else Claude should know about you or this project?\n"
            "   (your name, your company, time zone, deploy target, weird "
            "constraints — anything)"
        ),
        "default": "",
    },
]


def run_interview() -> dict:
    click.echo("")
    click.secho("I'll ask 7 quick questions. Hit Enter on any of them to skip.", fg="cyan")
    click.echo("")

    answers: dict = {}
    for q in QUESTIONS:
        click.echo(q["prompt"])
        default = q.get("default", "")
        suffix = f" [{default}]" if default else " (optional)"
        click.echo(f"   >{suffix}", nl=False)
        try:
            response = input(" ").strip()
        except EOFError:
            response = ""
        answers[q["key"]] = response or default
        click.echo("")

    return answers
