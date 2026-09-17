"""Persistent, adaptive review scheduling for practice attempts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


@dataclass(frozen=True)
class ReviewItem:
    id: int
    exercise: str
    prompt: str
    correct_answer: str
    user_answer: str
    mastery: int
    lapses: int


class ReviewDB:
    """Store attempts and schedule increasingly spaced review of every item."""

    _SUCCESS_INTERVALS = (
        timedelta(minutes=10),
        timedelta(days=1),
        timedelta(days=3),
        timedelta(days=7),
        timedelta(days=14),
        timedelta(days=30),
    )

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_key TEXT NOT NULL UNIQUE,
                language TEXT NOT NULL,
                exercise TEXT NOT NULL,
                prompt TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                user_answer TEXT NOT NULL,
                mastery INTEGER NOT NULL DEFAULT 0,
                lapses INTEGER NOT NULL DEFAULT 0,
                due_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_review_queue_due ON review_queue(language, due_at);"
        )
        self._conn.commit()

    def start_session(self) -> str:
        session_id = _timestamp(_utc_now())
        self._conn.execute(
            "INSERT OR REPLACE INTO sessions(session_id, started_at, ended_at) VALUES (?, ?, NULL);",
            (session_id, session_id),
        )
        self._conn.commit()
        return session_id

    def end_session(self, session_id: str) -> None:
        self._conn.execute("UPDATE sessions SET ended_at=? WHERE session_id=?;", (_timestamp(_utc_now()), session_id))
        self._conn.commit()

    def record_attempt(
        self,
        *,
        language: str,
        exercise: str,
        prompt: str,
        correct_answer: str,
        user_answer: str,
        correct: bool,
    ) -> None:
        """Record an attempt and schedule its next appearance by demonstrated mastery."""

        item_key = "\x1f".join((language, exercise, prompt, correct_answer))
        now = _utc_now()
        row = self._conn.execute(
            "SELECT id, mastery, lapses FROM review_queue WHERE item_key=?;", (item_key,)
        ).fetchone()
        if correct:
            previous_mastery = int(row[1]) if row else 0
            mastery = min(previous_mastery + 1, len(self._SUCCESS_INTERVALS))
            lapses = int(row[2]) if row else 0
            due_at = now + self._SUCCESS_INTERVALS[mastery - 1]
        else:
            mastery = 0
            lapses = (int(row[2]) if row else 0) + 1
            due_at = now

        values = (
            language,
            exercise,
            prompt,
            correct_answer,
            user_answer,
            mastery,
            lapses,
            _timestamp(due_at),
            _timestamp(now),
        )
        if row:
            self._conn.execute(
                """
                UPDATE review_queue
                SET language=?, exercise=?, prompt=?, correct_answer=?, user_answer=?, mastery=?, lapses=?, due_at=?, last_seen_at=?
                WHERE id=?;
                """,
                (*values, int(row[0])),
            )
        else:
            self._conn.execute(
                """
                INSERT INTO review_queue(
                    item_key, language, exercise, prompt, correct_answer, user_answer,
                    mastery, lapses, due_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (item_key, *values),
            )
        self._conn.commit()

    def due_items(self, *, language: str, limit: int = 20) -> list[ReviewItem]:
        rows = self._conn.execute(
            """
            SELECT id, exercise, prompt, correct_answer, user_answer, mastery, lapses
            FROM review_queue
            WHERE language=? AND due_at<=?
            ORDER BY lapses DESC, due_at ASC, id ASC
            LIMIT ?;
            """,
            (language, _timestamp(_utc_now()), limit),
        ).fetchall()
        return [ReviewItem(*(int(value) if index in {0, 5, 6} else str(value) for index, value in enumerate(row))) for row in rows]

    def close(self) -> None:
        self._conn.close()
