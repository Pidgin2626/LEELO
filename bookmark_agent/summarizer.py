"""Run the enriched bookmarks through Claude and produce data/summary.md.

Caches the bookmark corpus once (so the second pass — app ideas — is
cheap), uses adaptive thinking, and streams the response.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import anthropic

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
IN_FILE = DATA_DIR / "enriched.json"
OUT_FILE = DATA_DIR / "summary.md"

MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = """You analyze a user's saved X (Twitter) bookmarks and propose buildable software projects.

You will receive a JSON corpus of bookmarks. Each bookmark has:
  - text: the tweet body
  - linked_urls: referenced links
  - enrichment.fetched[]: full article text, YouTube transcripts, or GitHub READMEs

For each pass, follow the user's instructions exactly. Be concrete and specific — name real
tools, real APIs, and real problems the user appears to care about. Do not hedge."""


def format_corpus(enriched: list[dict]) -> str:
    parts: list[str] = []
    for i, bm in enumerate(enriched, 1):
        parts.append(f"--- BOOKMARK {i} (https://x.com/{bm.get('author', '?')}/status/{bm.get('id', '?')}) ---")
        parts.append(f"text: {bm.get('text', '').strip()}")
        for f in bm.get("enrichment", {}).get("fetched", []):
            kind = f.get("kind", "?")
            url = f.get("url", "")
            if f.get("error"):
                parts.append(f"  [{kind}] {url} (error: {f['error']})")
                continue
            if kind == "article":
                parts.append(f"  [article] {url}")
                parts.append(f"  title: {f.get('title', '')}")
                parts.append(f"  body: {f.get('text', '')[:6000]}")
            elif kind == "youtube_transcript":
                parts.append(f"  [yt] {url}")
                parts.append(f"  transcript: {f.get('text', '')[:8000]}")
            elif kind == "github_readme":
                parts.append(f"  [repo] {f.get('repo', '')}")
                parts.append(f"  readme: {f.get('text', '')[:4000]}")
        if bm.get("enrichment", {}).get("needs_manual_transcription"):
            parts.append("  [note: this bookmark contains video that wasn't transcribed]")
        parts.append("")
    return "\n".join(parts)


def run_pass(client: anthropic.Anthropic, corpus: str, instruction: str) -> str:
    with client.messages.stream(
        model=MODEL,
        max_tokens=32000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Here is the bookmark corpus:\n\n{corpus}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {"type": "text", "text": instruction},
                ],
            }
        ],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
        final = stream.get_final_message()

    text_parts = [b.text for b in final.content if b.type == "text"]
    print(
        f"\n[usage: input={final.usage.input_tokens}, "
        f"cache_read={final.usage.cache_read_input_tokens}, "
        f"cache_write={final.usage.cache_creation_input_tokens}, "
        f"output={final.usage.output_tokens}]",
        file=sys.stderr,
    )
    return "\n".join(text_parts)


THEMES_PROMPT = """First pass: themes.

Group these bookmarks into 5-10 distinct themes. For each theme:
- name it (3-5 words)
- list which bookmark numbers belong to it
- in 2-3 sentences, describe the underlying interest or problem the user keeps returning to

Return as markdown with `## Theme: <name>` headings."""


IDEAS_PROMPT = """Second pass: buildable app ideas.

Based on the themes you just identified, propose 5-15 concrete software applications the user
could build. For each idea, output exactly this format:

### App N: <short name>

- **One-line pitch**: <what it does in one sentence>
- **Motivating bookmarks**: <bookmark numbers that inspired this>
- **Core features** (3-5 bullets): <concrete features, not vague capabilities>
- **Stack**: <specific languages/frameworks/APIs to use>
- **Scope**: <small | medium | large> — <one sentence justifying>
- **First milestone**: <the smallest thing that would prove the idea works>

Order them by how strongly the bookmarks support the idea (strongest first). Skip ideas
that are speculative or only loosely connected to the bookmarks."""


def main(
    in_file: Path = IN_FILE,
    out_file: Path = OUT_FILE,
    label: str = "Bookmark Analysis",
    context_note: str = "",
) -> int:
    if not in_file.exists():
        print(f"Missing {in_file}. Run enricher.py first.", file=sys.stderr)
        return 1
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in your environment.", file=sys.stderr)
        return 1

    enriched = json.loads(in_file.read_text())
    if not enriched:
        out_file.write_text(
            f"# {label}\n\nNo bookmarks to summarize this run.\n"
        )
        print(f"Empty corpus, wrote a placeholder to {out_file}")
        return 0
    print(f"Summarizing {len(enriched)} bookmarks with {MODEL}.")

    corpus = format_corpus(enriched)
    print(f"Corpus size: {len(corpus):,} chars (~{len(corpus) // 4:,} tokens estimated)\n")

    client = anthropic.Anthropic()

    themes_prompt = THEMES_PROMPT
    ideas_prompt = IDEAS_PROMPT
    if context_note:
        themes_prompt = context_note + "\n\n" + THEMES_PROMPT
        ideas_prompt = context_note + "\n\n" + IDEAS_PROMPT

    print("\n=== PASS 1: THEMES ===\n")
    themes = run_pass(client, corpus, themes_prompt)

    print("\n\n=== PASS 2: APP IDEAS ===\n")
    ideas = run_pass(client, corpus, ideas_prompt)

    out_file.write_text(
        f"# {label}\n\nGenerated from {len(enriched)} bookmarks.\n\n"
        f"## Themes\n\n{themes}\n\n## App Ideas\n\n{ideas}\n"
    )
    print(f"\nWrote {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
