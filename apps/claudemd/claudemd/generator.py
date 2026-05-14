"""Call Claude to turn scanned facts + interview answers into a CLAUDE.md.

Streams the response so the user sees progress on long generations.
"""

from __future__ import annotations

import json
import sys

import anthropic

MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = """You write CLAUDE.md files for software projects.

A CLAUDE.md is the project-level system prompt that Claude Code reads automatically
when working in a directory. A great CLAUDE.md is:

- Concrete, not generic. Mention real files, real commands, real conventions.
- Short — under 200 lines unless the project is genuinely complex.
- Written for Claude as a colleague: directive ("use pytest, not unittest"),
  not aspirational ("we strive for excellence").
- Free of fluff. No "this project aims to..." marketing copy.

Standard sections (include only those that apply):

# <Project Name>
One-paragraph what-it-is.

## Stack
Bulleted languages, frameworks, key libraries.

## How to run / test / build
The literal commands.

## Project layout
What lives where, with one-line descriptions.

## Conventions
Naming, file structure, formatting tools, anything non-obvious.

## How to talk to me
Tone, skill level, style preferences.

## Never do
Hard rules — things Claude must refuse to do without confirmation.

## Notes
Anything else worth knowing — deploy target, weird constraints, where the docs live.
"""

USER_TEMPLATE = """Generate a CLAUDE.md for this project.

## Repository scan
{scan_json}

## User answers
{interview_json}

Write the CLAUDE.md now. Return only the markdown — no preamble, no
explanation, no triple-backtick wrapper around the whole thing."""


def generate(scan_result: dict, interview_result: dict) -> str:
    client = anthropic.Anthropic()

    user_text = USER_TEMPLATE.format(
        scan_json=json.dumps(scan_result, indent=2),
        interview_json=json.dumps(interview_result, indent=2),
    )

    chunks: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=16_000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
    ) as stream:
        for event in stream:
            if (
                event.type == "content_block_delta"
                and event.delta.type == "text_delta"
            ):
                chunks.append(event.delta.text)
                sys.stdout.write(event.delta.text)
                sys.stdout.flush()
        final = stream.get_final_message()

    print(
        f"\n\n[tokens used: input={final.usage.input_tokens}, "
        f"output={final.usage.output_tokens}]",
        file=sys.stderr,
    )
    return "".join(chunks).strip()


AUDIT_SYSTEM = """You audit existing CLAUDE.md files.

Look at the file the user provides and return a focused review in this exact
format:

## What works
- 2-4 bullets on what's good

## What's missing
- 2-5 bullets on important things not covered (run commands, conventions,
  layout, tone, things-to-never-do, etc.)

## What's too vague
- 2-4 bullets, each quoting the vague line and proposing a concrete rewrite

## Suggested additions
- A short code block with new sections/lines to copy in

Be direct. No "great start!" filler. Treat the user as a peer."""


def audit(existing_md: str, scan_result: dict) -> str:
    client = anthropic.Anthropic()
    user_text = (
        f"Here is the current CLAUDE.md:\n\n```markdown\n{existing_md}\n```\n\n"
        f"For context, here is a scan of the repo:\n\n"
        f"```json\n{json.dumps(scan_result, indent=2)}\n```"
    )

    chunks: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=8_000,
        thinking={"type": "adaptive"},
        system=AUDIT_SYSTEM,
        messages=[{"role": "user", "content": user_text}],
    ) as stream:
        for event in stream:
            if (
                event.type == "content_block_delta"
                and event.delta.type == "text_delta"
            ):
                chunks.append(event.delta.text)
                sys.stdout.write(event.delta.text)
                sys.stdout.flush()
        stream.get_final_message()
    return "".join(chunks).strip()
