from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from lang_practice.models import AttemptEvent
from lang_practice.planner import (
    PlannerItem, SessionState, catalog_for_language, load_planner_inputs, recommend_next,
)
from lang_practice.review_db import ReviewDB, ReviewItem


NOW = datetime(2026, 9, 28, 12, tzinfo=timezone.utc)
FIRST = lambda candidates: candidates[0]


def _event(state: SessionState, recommendation, *, outcome="correct", first_correct=True,
           support=frozenset(), number=1) -> AttemptEvent:
    return AttemptEvent(
        f"event-{number}", NOW, state.session_id, state.language,
        recommendation.destination_exercise_id or "review",
        recommendation.skill or "vocabulary", recommendation.direction or "target_to_english",
        recommendation.item_id or "legacy", outcome, True, support,
        "answer", first_correct,
    )


def _recommend(catalog, due, state, snapshots=None):
    return recommend_next(catalog, due, snapshots or {}, state, now=NOW, choose=FIRST)


def test_due_work_precedes_new_work_and_consumed_row_does_not_loop() -> None:
    catalog = (
        PlannerItem("french", "flashcard", "vocabulary", "target_to_english", "bonjour", "bonjour"),
        PlannerItem("french", "flashcard", "vocabulary", "target_to_english", "merci", "merci"),
    )
    due = [ReviewItem(4, "flashcard", "bonjour", "hello", "", 0, 1,
                      "v2\x1ffrench\x1fvocabulary\x1ftarget_to_english\x1fbonjour", "french")]
    state = SessionState("s", "french", new_item_limit=1)

    first = _recommend(catalog, due, state)
    assert (first.source, first.item_id, first.queue_id) == ("due", "bonjour", 4)
    state.record_result(first, _event(state, first))
    second = _recommend(catalog, due, state)
    assert (second.source, second.item_id) == ("new", "merci")
    state.record_result(second, _event(state, second, number=2))
    assert _recommend(catalog, due, state).source == "empty"


def test_miss_repairs_in_authored_sentence_without_immediate_repeat() -> None:
    catalog = (
        PlannerItem("italian", "flashcard", "vocabulary", "target_to_english", "pane", "pane"),
        PlannerItem("italian", "sentence", "sentence_translation", "target_to_english", "food_pane", "Mangio il pane."),
    )
    state = SessionState("s", "italian")
    first = _recommend(catalog, [], state)
    assert first.item_id == "pane"
    state.record_result(first, _event(state, first, outcome="incorrect", first_correct=False))

    repair = _recommend(catalog, [], state)
    assert (repair.source, repair.destination_exercise_id, repair.item_id) == ("repair", "sentence", "food_pane")
    assert repair.repair_target == first.key
    assert repair.support_level == "Supported"
    state.record_result(repair, _event(state, repair, number=2))
    assert _recommend(catalog, [], state).source == "empty"
    recap = state.recap()
    assert recap.first_try_successes == 1
    assert recap.first_try_attempts == 2
    assert recap.targets_to_revisit == (first.key,)


def test_new_load_is_bounded_but_learner_can_choose_focused_mode() -> None:
    catalog = tuple(
        PlannerItem("french", "flashcard", "vocabulary", "target_to_english", word, word)
        for word in ("bonjour", "merci", "pain")
    )
    state = SessionState("s", "french", new_item_limit=2)
    for number in (1, 2):
        recommendation = _recommend(catalog, [], state)
        assert recommendation.source == "new"
        state.record_result(recommendation, _event(state, recommendation, number=number))
    assert _recommend(catalog, [], state).source == "empty"
    state.choose_focused_mode("flashcard")
    assert _recommend(catalog, [], state).item_id == "pain"


def test_legacy_due_item_has_review_destination_and_unknown_proficiency() -> None:
    due = [ReviewItem(7, "Flashcards", "bonjour", "hello", "", 2, 0,
                      "french\x1fFlashcards\x1fbonjour\x1fhello", "french")]
    state = SessionState("s", "french")
    recommendation = _recommend(catalog_for_language("french"), due, state)
    assert (recommendation.destination_exercise_id, recommendation.item_id, recommendation.queue_id) == (
        "review", None, 7,
    )
    assert "unknown" in recommendation.reason
    state.record_result(recommendation)
    assert _recommend((), due, state).source == "empty"
    assert state.recap().skipped == 1


def test_empty_queue_has_actionable_reason() -> None:
    state = SessionState("s", "french")
    recommendation = _recommend((), (), state)
    assert recommendation.source == "empty"
    assert recommendation.destination_exercise_id is None
    assert "focused mode" in recommendation.reason


def test_language_isolation_and_guided_sentence_catalog() -> None:
    french = catalog_for_language("french")
    italian = catalog_for_language("italian")
    assert all(item.language == "french" for item in french)
    assert all(item.language == "italian" for item in italian)
    assert {item.item_id for item in italian if item.skill == "sentence_translation"} == {
        "greeting_ciao", "greeting_buongiorno", "food_pane", "home_gatto_casa"
    }
    state = SessionState("s", "french")
    with pytest.raises(ValueError, match="another language"):
        _recommend(italian, [], state)
    with pytest.raises(ValueError, match="another language"):
        _recommend(french, [ReviewItem(1, "x", "x", "x", "", 0, 0, "", "italian")], state)


def test_helped_attempts_recap_and_support_override() -> None:
    catalog = (PlannerItem("italian", "sentence", "sentence_translation", "target_to_english",
                           "food_pane", "Mangio il pane."),)
    state = SessionState("s", "italian")
    state.adjust_support("Independent")
    recommendation = _recommend(catalog, [], state)
    assert recommendation.support_level == "Independent"
    state.record_result(recommendation, _event(state, recommendation, support=frozenset({"hint"})))
    recap = state.recap()
    assert (recap.helped_attempts, recap.first_try_successes) == (1, 0)
    state.end_early()
    assert _recommend(catalog, [], state).source == "empty"


def test_one_day_success_does_not_create_lasting_sentence_readiness() -> None:
    with TemporaryDirectory() as directory:
        db = ReviewDB(Path(directory) / "review.sqlite3")
        try:
            session = db.start_session()
            for number in range(3):
                event = AttemptEvent(
                    f"success-{number}", NOW + timedelta(hours=number), session, "italian",
                    "flashcard", "vocabulary", "target_to_english", "pane", "correct", True,
                    frozenset(), "bread", True,
                )
                db.record_event(event, prompt="pane", correct_answer="bread")
            snapshot = db.readiness_snapshot(language="italian", skill="vocabulary",
                                             direction="target_to_english", item_id="pane")
            assert (snapshot.first_try_successes, snapshot.unaided_success_days) == (3, 1)
            catalog, due, snapshots = load_planner_inputs(db, "italian", now=NOW + timedelta(days=4))
            assert len(catalog) > 0
            assert snapshot == snapshots[("vocabulary", "target_to_english", "pane")]
            assert any(item.language == "italian" for item in due)
            assert not db.due_items(language="french", now=NOW + timedelta(days=4))
        finally:
            db.close()
