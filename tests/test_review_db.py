from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from lang_practice.languages.french.data import PRESENT_TENSE as FRENCH_FORMS
from lang_practice.languages.french.data import VOCABULARY as FRENCH_WORDS
from lang_practice.languages.italian.data import PRESENT_TENSE as ITALIAN_FORMS
from lang_practice.languages.italian.data import VOCABULARY as ITALIAN_WORDS
from lang_practice.models import AttemptEvent
from lang_practice.review_db import ReviewDB


class ReviewDBTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.path = Path(self.temp.name) / "review.sqlite3"
        self.databases: list[ReviewDB] = []

    def _open(self) -> ReviewDB:
        db = ReviewDB(self.path)
        self.databases.append(db)
        return db

    def tearDown(self) -> None:
        for db in self.databases:
            db.close()
        self.temp.cleanup()

    def _old_database(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("CREATE TABLE sessions(session_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, ended_at TEXT)")
            conn.execute(
                """CREATE TABLE review_queue(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, item_key TEXT NOT NULL UNIQUE,
                    language TEXT NOT NULL, exercise TEXT NOT NULL, prompt TEXT NOT NULL,
                    correct_answer TEXT NOT NULL, user_answer TEXT NOT NULL,
                    mastery INTEGER NOT NULL DEFAULT 0, lapses INTEGER NOT NULL DEFAULT 0,
                    due_at TEXT NOT NULL, last_seen_at TEXT NOT NULL)"""
            )
            conn.execute("INSERT INTO sessions VALUES ('old-session', '2024-01-01T00:00:00+00:00', NULL)")
            for language, prompt in (("french", "bonjour"), ("italian", "ciao")):
                conn.execute(
                    "INSERT INTO review_queue(item_key, language, exercise, prompt, correct_answer, user_answer, mastery, lapses, due_at, last_seen_at) "
                    "VALUES (?, ?, 'Flashcards', ?, 'hello', 'hello', 2, 1, '2024-01-02T00:00:00+00:00', '2024-01-01T00:00:00+00:00')",
                    (f"{language}\x1fFlashcards\x1f{prompt}\x1fhello", language, prompt),
                )
        conn.close()

    def test_old_schema_migrates_idempotently_without_inventing_history(self) -> None:
        self._old_database()
        for _ in range(2):
            db = self._open()
            self.assertEqual([item.prompt for item in db.due_items(language="french")], ["bonjour"])
            self.assertEqual([item.prompt for item in db.due_items(language="italian")], ["ciao"])
            self.assertEqual(db.attempts(language="french"), [])
            self.assertEqual(db.readiness_snapshot(language="french", skill="vocabulary", direction="target_to_english", item_id="bonjour").first_try_attempts, 0)
            db.close()
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], ReviewDB.SCHEMA_VERSION)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM review_queue").fetchone()[0], 2)
            self.assertEqual(conn.execute("SELECT mastery, lapses FROM review_queue WHERE language='french'").fetchone(), (2, 1))
        conn.close()

    def test_attempts_survive_restart_and_are_isolated_by_language(self) -> None:
        db = self._open()
        session = db.start_session()
        now = datetime.now(timezone.utc)
        french = AttemptEvent("f-1", now, session, "french", "flashcard", "vocabulary",
                              "target_to_english", "bonjour", "incorrect", True,
                              frozenset(), "goodbye")
        italian = AttemptEvent("i-1", now, session, "italian", "flashcard", "vocabulary",
                               "target_to_english", "ciao", "correct", False,
                               frozenset({"hint"}), "hello", False)
        self.assertTrue(db.record_event(french, prompt="bonjour", correct_answer="hello"))
        self.assertTrue(db.record_event(italian, prompt="ciao", correct_answer="hello"))
        self.assertFalse(db.record_event(french, prompt="bonjour", correct_answer="hello"))
        self.assertNotEqual(session, db.start_session())
        db.close()  # Simulate an interrupted launch with an open session.

        db = self._open()
        self.assertEqual(db.attempts(language="french"), [french])
        self.assertEqual(db.attempts(language="italian"), [italian])
        self.assertEqual([item.prompt for item in db.due_items(language="french")], ["bonjour"])
        self.assertEqual([item.prompt for item in db.due_items(language="italian")], ["ciao"])
        french_snapshot = db.readiness_snapshot(language="french", skill="vocabulary",
                                                direction="target_to_english", item_id="bonjour")
        self.assertEqual((french_snapshot.first_try_attempts, french_snapshot.first_try_successes,
                          french_snapshot.recent_misses), (1, 0, 1))
        self.assertIsNotNone(french_snapshot.due_at)
        italian_snapshot = db.readiness_snapshot(language="italian", skill="vocabulary",
                                                 direction="target_to_english", item_id="ciao")
        self.assertEqual((italian_snapshot.first_try_attempts, italian_snapshot.first_try_successes,
                          italian_snapshot.assisted_attempts), (1, 0, 1))
        self.assertEqual(italian_snapshot.recent_misses, 1)
        db.close()

    def test_history_is_append_only_and_rejects_unknown_session(self) -> None:
        db = self._open()
        now = datetime.now(timezone.utc)
        event = AttemptEvent("f-1", now, "missing-session", "french", "flashcard",
                             "vocabulary", "target_to_english", "bonjour", "correct", True,
                             frozenset(), "hello", True)
        with self.assertRaises(sqlite3.IntegrityError):
            db.record_event(event, prompt="bonjour", correct_answer="hello")
        self.assertEqual(db.attempts(language="french"), [])
        self.assertEqual(db.due_items(language="french"), [])

        event = AttemptEvent("f-1", now, db.start_session(), "french", "flashcard",
                             "vocabulary", "target_to_english", "bonjour", "correct", True,
                             frozenset(), "hello", True)
        self.assertTrue(db.record_event(event, prompt="bonjour", correct_answer="hello"))
        with self.assertRaises(sqlite3.IntegrityError):
            db._conn.execute("UPDATE attempt_events SET answer='changed' WHERE event_id='f-1'")
        with self.assertRaises(sqlite3.IntegrityError):
            db._conn.execute("DELETE FROM attempt_events WHERE event_id='f-1'")
        self.assertEqual(db.attempts(language="french"), [event])

    def test_helped_first_response_is_not_unaided_success(self) -> None:
        db = self._open()
        event = AttemptEvent("helped", datetime.now(timezone.utc), db.start_session(),
                             "french", "flashcard", "vocabulary", "target_to_english",
                             "merci", "correct", True, frozenset({"hint"}), "thank you", True)
        db.record_event(event, prompt="merci", correct_answer="thank you")
        snapshot = db.readiness_snapshot(language="french", skill="vocabulary",
                                         direction="target_to_english", item_id="merci")
        self.assertEqual((snapshot.first_try_attempts, snapshot.first_try_successes,
                          snapshot.assisted_attempts), (1, 0, 1))
        self.assertEqual([item.prompt for item in db.due_items(language="french")], ["merci"])

    def test_legacy_review_path_remains_usable(self) -> None:
        self._old_database()
        db = self._open()
        db.record_attempt(language="french", exercise="Flashcards", prompt="bonjour",
                          correct_answer="hello", user_answer="hello", correct=True)
        self.assertEqual(db.attempts(language="french"), [])
        self.assertEqual(db.due_items(language="french"), [])
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM review_queue").fetchone()[0], 2)
        conn.close()
        db.close()

    def test_multiple_choice_review_reschedules_same_stable_row(self) -> None:
        db = self._open()
        event = AttemptEvent("miss", datetime.now(timezone.utc), db.start_session(),
                             "french", "flashcard", "vocabulary", "target_to_english",
                             "bonjour", "incorrect", True, frozenset(), "goodbye", False)
        db.record_event(event, prompt="bonjour", correct_answer="hello")
        item = db.due_items(language="french")[0]
        db.resolve_review_item(item, user_answer="hello", correct=True)
        self.assertEqual(db.attempts(language="french"), [event])
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM review_queue").fetchone()[0], 1)
        conn.close()

    def test_authored_ids_are_unique_per_language_and_forms_use_canonical_person(self) -> None:
        for words, forms in ((FRENCH_WORDS, FRENCH_FORMS), (ITALIAN_WORDS, ITALIAN_FORMS)):
            word_ids = [word.id for word in words]
            form_ids = [form.id for form in forms]
            self.assertTrue(all(word_ids + form_ids))
            self.assertEqual(len(word_ids), len(set(word_ids)))
            self.assertEqual(len(form_ids), len(set(form_ids)))
            self.assertTrue(forms[0].form_id("first_singular").endswith(":present:first_singular"))
            with self.assertRaises(ValueError):
                forms[0].form_id("je")


if __name__ == "__main__":
    unittest.main()
