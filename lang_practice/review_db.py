"""Persistent, adaptive review scheduling for practice attempts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from .models import AttemptEvent, ReadinessSnapshot


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Attempt timestamps must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _parse_timestamp(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


@dataclass(frozen=True)
class ReviewItem:
    id: int
    exercise: str
    prompt: str
    correct_answer: str
    user_answer: str
    mastery: int
    lapses: int
    item_key: str = ""
    language: str = ""


class ReviewDB:
    """Keep scheduling state separate from append-only learning evidence."""

    SCHEMA_VERSION = 1

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
        try:
            self._conn.execute("PRAGMA foreign_keys=ON;")
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._ensure_schema()
        except Exception:
            self._conn.close()
            raise

    def _ensure_schema(self) -> None:
        version = int(self._conn.execute("PRAGMA user_version").fetchone()[0])
        if version > self.SCHEMA_VERSION:
            raise RuntimeError(f"Review database schema {version} is newer than this app supports")
        # sqlite3's context manager does not begin a transaction for DDL.
        # Begin explicitly so an interrupted migration cannot leave a partial schema.
        self._conn.execute("BEGIN IMMEDIATE")
        with self._conn:
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
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS attempt_events (
                    event_id TEXT PRIMARY KEY,
                    occurred_at TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    language TEXT NOT NULL,
                    exercise_id TEXT NOT NULL,
                    skill TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    outcome TEXT NOT NULL CHECK(outcome IN ('correct', 'incorrect', 'skipped')),
                    first_try INTEGER NOT NULL CHECK(first_try IN (0, 1)),
                    first_try_correct INTEGER CHECK(first_try_correct IN (0, 1)),
                    support_used TEXT NOT NULL,
                    answer TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_attempt_target ON attempt_events(language, skill, direction, item_id, occurred_at);"
            )
            self._conn.execute(
                """CREATE TRIGGER IF NOT EXISTS attempt_events_no_update
                BEFORE UPDATE ON attempt_events BEGIN
                    SELECT RAISE(ABORT, 'attempt history is append-only');
                END"""
            )
            self._conn.execute(
                """CREATE TRIGGER IF NOT EXISTS attempt_events_no_delete
                BEFORE DELETE ON attempt_events BEGIN
                    SELECT RAISE(ABORT, 'attempt history is append-only');
                END"""
            )
            self._conn.execute(f"PRAGMA user_version={self.SCHEMA_VERSION}")

    def start_session(self) -> str:
        # A launch is distinct even if it starts in the same clock tick. Never
        # replace a prior session, including one left open by a crash.
        session_id = uuid4().hex
        self._conn.execute(
            "INSERT INTO sessions(session_id, started_at, ended_at) VALUES (?, ?, NULL);",
            (session_id, _timestamp(_utc_now())),
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
        """Legacy GUI scheduling path; it does not invent detailed attempt evidence."""

        item_key = "\x1f".join((language, exercise, prompt, correct_answer))
        with self._conn:
            self._schedule(item_key, language, exercise, prompt, correct_answer, user_answer, correct, _utc_now())

    def resolve_review_item(self, item: ReviewItem, *, user_answer: str, correct: bool) -> None:
        """Reschedule the same due row after multiple-choice review.

        A multiple-choice result is not equivalent to an unaided typed answer,
        so it changes scheduling without inventing a target-skill event.
        """

        with self._conn:
            row = self._conn.execute(
                "SELECT item_key, language, exercise, prompt, correct_answer FROM review_queue WHERE id=?",
                (item.id,),
            ).fetchone()
            if row is None:
                raise ValueError("Review item is no longer in the queue")
            if item.language and row[1] != item.language:
                raise ValueError("Review item language changed")
            self._schedule(row[0], row[1], row[2], row[3], row[4], user_answer, correct, _utc_now())

    def _schedule(
        self,
        item_key: str,
        language: str,
        exercise: str,
        prompt: str,
        correct_answer: str,
        user_answer: str,
        correct: bool,
        now: datetime,
    ) -> None:
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

    def record_event(self, event: AttemptEvent, *, prompt: str, correct_answer: str) -> bool:
        """Append one event and update its due state atomically.

        Reusing an event ID after an interrupted write is a no-op. The return
        value says whether a new event was stored.
        """

        if event.outcome not in {"correct", "incorrect", "skipped"}:
            raise ValueError(f"Unknown outcome: {event.outcome}")
        if event.first_try_correct is not None and not isinstance(event.first_try_correct, bool):
            raise ValueError("First-try result must be true, false, or unknown")
        if event.first_try_correct is True and (not event.first_try or event.outcome != "correct"):
            raise ValueError("A first-try success must resolve correctly on the first response")
        if event.first_try_correct is False and event.first_try and event.outcome == "correct":
            raise ValueError("A first-try result conflicts with the resolved outcome")
        if not all((event.event_id, event.session_id, event.language, event.exercise_id,
                    event.skill, event.direction, event.item_id)):
            raise ValueError("Attempt identity fields must be nonempty")
        if not event.support_used <= {"hint", "reveal"}:
            raise ValueError("Unknown support flag")
        occurred_at = _timestamp(event.occurred_at)
        with self._conn:
            inserted = self._conn.execute(
                """
                INSERT OR IGNORE INTO attempt_events(
                    event_id, occurred_at, session_id, language, exercise_id, skill,
                    direction, item_id, outcome, first_try, first_try_correct, support_used, answer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (event.event_id, occurred_at, event.session_id, event.language,
                 event.exercise_id, event.skill, event.direction, event.item_id,
                 event.outcome, int(event.first_try),
                 None if event.first_try_correct is None else int(event.first_try_correct),
                 json.dumps(sorted(event.support_used)),
                 event.answer),
            ).rowcount
            if inserted:
                item_key = "\x1f".join(("v2", event.language, event.skill, event.direction, event.item_id))
                unaided_success = (event.outcome == "correct" and event.first_try
                                   and event.first_try_correct is not False and not event.support_used)
                self._schedule(item_key, event.language, event.exercise_id, prompt,
                               correct_answer, event.answer or "", unaided_success,
                               event.occurred_at)
        return bool(inserted)

    def attempts(
        self, *, language: str, skill: str | None = None,
        direction: str | None = None, item_id: str | None = None,
    ) -> list[AttemptEvent]:
        """Read new evidence in chronological order for one language."""

        clauses = ["language=?"]
        params: list[str] = [language]
        for column, value in (("skill", skill), ("direction", direction), ("item_id", item_id)):
            if value is not None:
                clauses.append(f"{column}=?")
                params.append(value)
        rows = self._conn.execute(
            "SELECT event_id, occurred_at, session_id, language, exercise_id, skill, "
            "direction, item_id, outcome, first_try, support_used, answer, first_try_correct "
            f"FROM attempt_events WHERE {' AND '.join(clauses)} ORDER BY occurred_at, rowid",
            params,
        ).fetchall()
        return [AttemptEvent(row[0], datetime.fromisoformat(row[1]), *row[2:9],
                             bool(row[9]), frozenset(json.loads(row[10])), row[11],
                             None if row[12] is None else bool(row[12])) for row in rows]

    def readiness_snapshot(
        self, *, language: str, skill: str, direction: str, item_id: str,
    ) -> ReadinessSnapshot:
        """Derive proficiency evidence from events; legacy queue rows stay unknown."""

        events = self.attempts(language=language, skill=skill, direction=direction, item_id=item_id)
        item_key = "\x1f".join(("v2", language, skill, direction, item_id))
        row = self._conn.execute("SELECT due_at FROM review_queue WHERE item_key=?", (item_key,)).fetchone()
        first_results = [
            (e.first_try_correct if e.first_try_correct is not None else e.outcome == "correct")
            and not e.support_used
            for e in events if e.first_try_correct is not None or
            (e.first_try and not e.support_used and e.outcome != "skipped")
        ]
        return ReadinessSnapshot(
            language=language, skill=skill, direction=direction, item_id=item_id,
            first_try_successes=sum(first_results),
            first_try_attempts=len(first_results),
            assisted_attempts=sum("hint" in e.support_used for e in events),
            revealed_attempts=sum("reveal" in e.support_used for e in events),
            recent_misses=sum(e.outcome != "correct" or e.first_try_correct is False for e in events[-5:]),
            last_attempt_at=events[-1].occurred_at if events else None,
            due_at=_parse_timestamp(row[0]) if row else None,
            unaided_success_days=len({
                e.occurred_at.astimezone(timezone.utc).date()
                for e in events
                if e.first_try and e.outcome == "correct"
                and e.first_try_correct is not False and not e.support_used
            }),
        )

    def due_items(self, *, language: str, limit: int = 20, now: datetime | None = None) -> list[ReviewItem]:
        rows = self._conn.execute(
            """
            SELECT id, exercise, prompt, correct_answer, user_answer, mastery, lapses, item_key, language
            FROM review_queue
            WHERE language=? AND due_at<=?
            ORDER BY lapses DESC, due_at ASC, id ASC
            LIMIT ?;
            """,
            (language, _timestamp(now or _utc_now()), limit),
        ).fetchall()
        return [ReviewItem(*(int(value) if index in {0, 5, 6} else str(value) for index, value in enumerate(row))) for row in rows]

    def close(self) -> None:
        self._conn.close()
