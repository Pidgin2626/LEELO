"""Extra analyses over the enriched bookmark corpus.

python analyzer.py tools           -> data/tools.md
python analyzer.py contradictions  -> data/contradictions.md

Reuses format_corpus + model choice from summarizer.py so the input
shape stays consistent. Streams Claude's output to your terminal so
you can watch it work.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic

from summarizer import MODEL, format_corpus

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
ENRICHED = DATA_DIR / "enriched.json"

SYSTEM_PROMPT = """You analyze bookmark corpora to extract specific, actionable, structured information.

Rules:
- Be concrete. Name specific tools, quote specific text, cite specific bookmark numbers.
- Never invent things not present in the corpus.
- Skip generic filler. If the corpus doesn't support a claim, say so instead of hedging."""


TOOLS_PROMPT = """Extract every tool, product, service, API, library, framework, or platform mentioned across these bookmarks.

Include: named commercial products (Notion, Whoop), APIs (Meta Ads API, Plaid, Serper), MCP servers (github-mcp, meta-ads-mcp, filesystem-mcp), open-source libraries (Chatterbox Turbo, Playwright, LangGraph), platforms (Cofounder 2, Cursor, Firebase Studio), CLI tools (yt-dlp, ffmpeg), and hosted services (Instantly, Smartlead, HubSpot).

Do NOT include: generic concepts ("a database", "an LLM", "vector search"), Claude itself, or Anthropic products the user already uses (Claude Code, Claude Projects — unless a specific mode like Cowork is being called out).

Dedupe aggressively — "Meta Ads MCP" and "the Meta Ads MCP" and "meta-ads-mcp" are one tool.

Output format:

# Tool Shopping List

## Start here — top 5

A short callout ranking the 5 tools you should try FIRST this week, based on:
(a) how many times they appear in the bookmarks × (b) how central to the user's dominant themes (Claude power-user setup, agent-driven marketing, local-service lead gen, second-brain workflows) × (c) how fast the user can get a first useful result.

For each of the top 5:
- **Tool name** — one-line pitch
- **This week's action**: one specific concrete step ("sign up for Instantly free trial and export one lead list of 50 roofers"). Not "explore Instantly."

## Full list (alphabetical)

Then for every tool found, in alphabetical order:

### <Tool Name>
- **What it does**: <one plain-English sentence>
- **Category**: <MCP server | API | SaaS product | open-source library | hosted platform | CLI tool | other>
- **Cost tier**: <free | freemium | cheap $/mo | expensive $$$/mo | enterprise | unknown>
- **Mentioned in bookmarks**: <list of bookmark numbers>
- **Why you'd care**: <one sentence tying it to one of the user's themes>
- **Setup effort**: <trivial | medium | heavy>

End with a short **Skip list** — tools mentioned that the user should NOT waste time on given their profile, with one-sentence reasons."""


CONTRADICTIONS_PROMPT = """Find open questions where the accounts the user follows disagree with each other. Real disagreements only — not complementary advice.

Examples of REAL contradictions:
- Bookmark A says "always use adaptive thinking on Claude"; Bookmark B says "adaptive thinking wastes tokens, disable it."
- Bookmark A recommends one gigantic CLAUDE.md; Bookmark B recommends splitting into 8 small files.

Examples of NON-contradictions (skip these):
- "Use pytest" vs "use unittest" (both work; not an argument).
- One tweet about Meta Ads and another about Google Ads (different topics).
- Different tools solving different problems.

Output format:

# Contradictions in Your Bookmarks

If you find fewer than 3 genuine contradictions, say so at the top and list only what you found. Do not pad.

For each contradiction:

## <One-sentence question the contradiction implicitly poses>

- **What's at stake**: <one sentence — why answering it right matters for the user's goals>
- **Position A**: <quote or tight paraphrase, cite bookmark number(s) and author>
- **Position B**: <quote or tight paraphrase, cite bookmark number(s) and author>
- **My read**: <one paragraph — which position is stronger given the user's specific themes, and what evidence or test would settle it definitively>

Order by: which contradictions block a decision the user is likely about to make in the next month."""


def run_analysis(corpus: str, instruction: str, out_file: Path) -> str:
    client = anthropic.Anthropic()

    chunks: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=16_000,
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
            if (
                event.type == "content_block_delta"
                and event.delta.type == "text_delta"
            ):
                chunks.append(event.delta.text)
                sys.stdout.write(event.delta.text)
                sys.stdout.flush()
        final = stream.get_final_message()

    result = "".join(chunks).strip()
    out_file.write_text(result + "\n", encoding="utf-8")
    print(
        f"\n\n[usage: input={final.usage.input_tokens}, "
        f"cache_read={final.usage.cache_read_input_tokens}, "
        f"cache_write={final.usage.cache_creation_input_tokens}, "
        f"output={final.usage.output_tokens}]"
    )
    print(f"Wrote {out_file}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("tools", help="Extract every tool/API mentioned, ranked.")
    sub.add_parser("contradictions", help="Find topics your sources disagree on.")
    args = parser.parse_args()

    if not ENRICHED.exists():
        print(f"Missing {ENRICHED}. Run `python run.py` first.", file=sys.stderr)
        return 1
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in your environment.", file=sys.stderr)
        return 1

    enriched = json.loads(ENRICHED.read_text(encoding="utf-8"))
    corpus = format_corpus(enriched)
    print(
        f"Analyzing {len(enriched)} bookmarks (~{len(corpus) // 4:,} tokens) "
        f"with {MODEL}.\n"
    )

    if args.command == "tools":
        run_analysis(corpus, TOOLS_PROMPT, DATA_DIR / "tools.md")
    elif args.command == "contradictions":
        run_analysis(corpus, CONTRADICTIONS_PROMPT, DATA_DIR / "contradictions.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
