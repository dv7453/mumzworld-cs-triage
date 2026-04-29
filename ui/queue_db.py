"""SQLite-backed queue storage for the Streamlit dashboard.

This is designed for demo/dev usage: simple schema, no external services required.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class QueueItem:
    id: str
    created_at: str
    urgency: int
    intent: str
    language: str
    sentiment: str
    email_text: str
    triage_json: dict[str, Any]
    debug_trace: dict[str, Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def init_db(db_path: str = "queue.db") -> None:
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS queue_items (
              id TEXT PRIMARY KEY,
              created_at TEXT NOT NULL,
              urgency INTEGER NOT NULL,
              intent TEXT NOT NULL,
              language TEXT NOT NULL,
              sentiment TEXT NOT NULL,
              email_text TEXT NOT NULL,
              triage_json TEXT NOT NULL,
              debug_trace TEXT NOT NULL
            )
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_queue_urgency ON queue_items(urgency)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_queue_created ON queue_items(created_at)")
        con.commit()
    finally:
        con.close()


def upsert_item(*, item: QueueItem, db_path: str = "queue.db") -> None:
    init_db(db_path=db_path)
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            """
            INSERT OR REPLACE INTO queue_items
              (id, created_at, urgency, intent, language, sentiment, email_text, triage_json, debug_trace)
            VALUES
              (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                item.created_at,
                int(item.urgency),
                item.intent,
                item.language,
                item.sentiment,
                item.email_text,
                json.dumps(item.triage_json, ensure_ascii=False),
                json.dumps(item.debug_trace, ensure_ascii=False),
            ),
        )
        con.commit()
    finally:
        con.close()


def list_items(*, db_path: str = "queue.db") -> list[QueueItem]:
    init_db(db_path=db_path)
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute(
            """
            SELECT id, created_at, urgency, intent, language, sentiment, email_text, triage_json, debug_trace
            FROM queue_items
            ORDER BY urgency DESC, created_at DESC
            """
        ).fetchall()
    finally:
        con.close()

    out: list[QueueItem] = []
    for (
        _id,
        created_at,
        urgency,
        intent,
        language,
        sentiment,
        email_text,
        triage_json,
        debug_trace,
    ) in rows:
        out.append(
            QueueItem(
                id=_id,
                created_at=created_at,
                urgency=int(urgency),
                intent=str(intent),
                language=str(language),
                sentiment=str(sentiment),
                email_text=str(email_text),
                triage_json=json.loads(triage_json),
                debug_trace=json.loads(debug_trace),
            )
        )
    return out


def get_item(*, item_id: str, db_path: str = "queue.db") -> QueueItem | None:
    init_db(db_path=db_path)
    con = sqlite3.connect(db_path)
    try:
        row = con.execute(
            """
            SELECT id, created_at, urgency, intent, language, sentiment, email_text, triage_json, debug_trace
            FROM queue_items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()
    finally:
        con.close()

    if not row:
        return None

    (
        _id,
        created_at,
        urgency,
        intent,
        language,
        sentiment,
        email_text,
        triage_json,
        debug_trace,
    ) = row
    return QueueItem(
        id=_id,
        created_at=created_at,
        urgency=int(urgency),
        intent=str(intent),
        language=str(language),
        sentiment=str(sentiment),
        email_text=str(email_text),
        triage_json=json.loads(triage_json),
        debug_trace=json.loads(debug_trace),
    )


def db_exists(db_path: str = "queue.db") -> bool:
    return Path(db_path).exists()


def make_id(prefix: str) -> str:
    # Human-friendly ids for demo recordings.
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{ts}"


def utc_now_iso() -> str:
    return _utc_now_iso()

