"""Run the full pipeline: export -> enrich -> summarize.

Each step is idempotent. Re-running picks up where the previous one left off.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).parent

import exporter
import enricher
import summarizer


def main() -> int:
    print("=" * 60)
    print("STEP 1: Exporting bookmarks from X (browser will open)")
    print("=" * 60)
    if asyncio.run(exporter.main()) != 0:
        return 1

    print("\n" + "=" * 60)
    print("STEP 2: Enriching bookmarks (articles, transcripts, READMEs)")
    print("=" * 60)
    if enricher.main() != 0:
        return 1

    print("\n" + "=" * 60)
    print("STEP 3: Summarizing with Claude")
    print("=" * 60)
    return summarizer.main()


if __name__ == "__main__":
    sys.exit(main())
