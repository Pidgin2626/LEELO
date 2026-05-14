"""SQLite-backed decision log.

Lives at ~/.council/decisions.db. One row per question asked.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .orchestrator import CouncilResult

DB_DIR = Path(os.environ.get("COUNCIL_HOME", Path.home() / ".council"))
DB_FILE = DB_DIR / "decisions.db"


def _connect() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            question TEXT NOT NULL,
            advisors_json TEXT NOT NULL,
            synthesis TEXT NOT NULL,
            transcript_md TEXT NOT NULL
        )
        """
    )
    return conn


def save(result: CouncilResult) -> int:
    conn = _connect()
    try:
        advisors = [
            {
                "name": s.advisor.name,
                "model_id": getattr(s.advisor, "model_id", ""),
                "persona": s.persona.name,
            }
            for s in result.seats
        ]
        cur = conn.execute(
            "INSERT INTO decisions (created_at, question, advisors_json, "
            "synthesis, transcript_md) VALUES (?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                result.question,
                json.dumps(advisors),
                result.synthesis,
                result.transcript_md,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_decisions(limit: int = 25) -> list[dict]:
    conn = _connect()
    try:
        cur = conn.execute(
            "SELECT id, created_at, question FROM decisions "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [
            {"id": r[0], "created_at": r[1], "question": r[2]}
            for r in cur.fetchall()
        ]
    finally:
        conn.close()


def get(decision_id: int) -> dict | None:
    conn = _connect()
    try:
        cur = conn.execute(
            "SELECT id, created_at, question, advisors_json, synthesis, "
            "transcript_md FROM decisions WHERE id = ?",
            (decision_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "created_at": row[1],
            "question": row[2],
            "advisors": json.loads(row[3]),
            "synthesis": row[4],
            "transcript_md": row[5],
        }
    finally:
        conn.close()
