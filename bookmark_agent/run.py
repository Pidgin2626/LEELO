"""Run the pipeline. Two modes:

  python run.py                # full run: export -> enrich all -> summarize all
  python run.py --incremental  # export -> enrich only NEW bookmarks since last run
                               # -> write a summary of just the new ones
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

import enricher
import exporter
import state
import summarizer


def _run_export() -> int:
    print("=" * 60)
    print("STEP 1: Exporting bookmarks from X (browser will open)")
    print("=" * 60)
    return asyncio.run(exporter.main())


def _run_full() -> int:
    if _run_export() != 0:
        return 1

    print("\n" + "=" * 60)
    print("STEP 2: Enriching all bookmarks")
    print("=" * 60)
    if enricher.main() != 0:
        return 1

    print("\n" + "=" * 60)
    print("STEP 3: Summarizing with Claude")
    print("=" * 60)
    rc = summarizer.main()
    if rc != 0:
        return rc

    # Record every ID as seen so the next incremental run has a baseline.
    bookmarks = json.loads((DATA_DIR / "bookmarks.json").read_text(encoding="utf-8"))
    seen = state.load_seen() | {bm["id"] for bm in bookmarks}
    state.save_seen(seen)
    print(f"\nMarked {len(seen)} total IDs as seen.")
    return 0


def _run_incremental() -> int:
    if _run_export() != 0:
        return 1

    all_bookmarks = json.loads((DATA_DIR / "bookmarks.json").read_text(encoding="utf-8"))
    seen = state.load_seen()
    new_bookmarks = [bm for bm in all_bookmarks if bm["id"] not in seen]

    print("\n" + "=" * 60)
    print(
        f"DIFF: {len(all_bookmarks)} total on X, {len(seen)} already seen, "
        f"{len(new_bookmarks)} new."
    )
    print("=" * 60)

    if not new_bookmarks:
        print("\nNo new bookmarks since last run. Nothing to do.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    new_in = DATA_DIR / f"bookmarks-new-{stamp}.json"
    new_enriched = DATA_DIR / f"enriched-new-{stamp}.json"
    new_summary = DATA_DIR / f"summary-new-{stamp}.md"

    new_in.write_text(json.dumps(new_bookmarks, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(new_bookmarks)} new bookmarks to {new_in.name}")

    print("\n" + "=" * 60)
    print("STEP 2: Enriching only new bookmarks")
    print("=" * 60)
    if enricher.main(in_file=new_in, out_file=new_enriched) != 0:
        return 1

    print("\n" + "=" * 60)
    print("STEP 3: Summarizing new bookmarks with Claude")
    print("=" * 60)
    context = (
        f"NOTE: These are the {len(new_bookmarks)} NEW bookmarks the user "
        f"saved since the last run. They already have a broader picture from "
        f"a previous summary — focus your themes and app ideas on what these "
        f"specific new saves add or shift."
    )
    rc = summarizer.main(
        in_file=new_enriched,
        out_file=new_summary,
        label=f"New Bookmarks — {stamp}",
        context_note=context,
    )
    if rc != 0:
        return rc

    seen |= {bm["id"] for bm in new_bookmarks}
    state.save_seen(seen)
    print(f"\nMarked {len(seen)} total IDs as seen. Summary at {new_summary}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only process bookmarks new since the last run.",
    )
    args = parser.parse_args()
    return _run_incremental() if args.incremental else _run_full()


if __name__ == "__main__":
    sys.exit(main())
