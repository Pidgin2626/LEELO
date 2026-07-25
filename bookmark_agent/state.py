"""Persistent record of which bookmark IDs we've already enriched.

Lives at state/seen_ids.json. Loading a missing file returns an empty set
(so a first incremental run treats every current bookmark as new).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent
STATE_DIR = ROOT / "state"
SEEN_FILE = STATE_DIR / "seen_ids.json"


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    try:
        return set(json.loads(SEEN_FILE.read_text()))
    except Exception:
        return set()


def save_seen(ids: set[str]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(sorted(ids), indent=2))
