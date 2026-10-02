from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from lang_practice.exercises import ConjugationExercise, FlashcardExercise, PromptAttemptState, SentencePracticeExercise
from lang_practice.gui import ConjugationTab, FlashcardTab, LangPracticeApp, SentencePracticeTab, SessionMetrics
from lang_practice.models import AttemptResolution, ConjugationPattern, Sentence, VocabularyItem
from lang_practice.review_db import ReviewDB


@dataclass
class _Value:
    value: str

    def get(self) -> str:
        return self.value


def test_prompt_attempt_state_resolves_once_after_retries_and_help() -> None:
    state = PromptAttemptState()
    state.note_answer("wrong", False)
    state.mark_support("hint")
    state.note_answer("right", True)

    evidence = state.resolve("correct", "right")

    assert evidence == (False, frozenset({"hint"}), False, "right")
    assert state.resolve("correct", "right") is None


def test_flashcard_emits_distinct_target_production_direction_once() -> None:
    captured: list[AttemptResolution] = []
    tab = FlashcardTab.__new__(FlashcardTab)
    tab._attempt_state = PromptAttemptState()
    tab.direction_var = _Value("English → target")
    tab._prompt_direction = "english_to_target"
    tab._on_resolution = captured.append
    item = VocabularyItem("bonjour", "hello", language="french", id="bonjour")

    tab._attempt_state.note_answer("bonjour", True)
    tab._emit_resolution(item, "correct", "bonjour")
    tab._emit_resolution(item, "correct", "bonjour")

    assert len(captured) == 1
    resolution = captured[0]
    assert (resolution.skill, resolution.direction, resolution.item_id) == (
        "vocabulary", "english_to_target", "bonjour",
    )
    assert resolution.prompt == "hello"
    assert resolution.correct_answer == "bonjour"


def test_conjugation_emits_canonical_verb_form_not_display_prompt() -> None:
    captured: list[AttemptResolution] = []
    pattern = ConjugationPattern(
        "parlare", "to speak", "parlo", "parli", "parla", "parliamo", "parlate", "parlano",
        language="italian", id="parlare",
    )
    exercise = ConjugationExercise(current_pattern=pattern, current_index=4)
    tab = ConjugationTab.__new__(ConjugationTab)
    tab.exercise = exercise
    tab._attempt_state = PromptAttemptState()
    tab._on_resolution = captured.append
    tab.phrase_var = _Value("Voi ______ (parlare)")

    tab._attempt_state.note_answer("parlate", True)
    tab._emit_resolution("correct", "parlate")

    assert len(captured) == 1
    resolution = captured[0]
    assert (resolution.skill, resolution.direction, resolution.item_id) == (
        "verb_form", "target_form", "parlare:present:second_plural",
    )
    assert resolution.prompt == "Voi ______ (parlare)"


def test_sentence_reveal_is_one_supported_skipped_resolution() -> None:
    captured: list[AttemptResolution] = []
    sentence = Sentence("ciao", "Ciao.", "Hello.", language="italian")
    exercise = SentencePracticeExercise.__new__(SentencePracticeExercise)
    exercise.current_sentence = sentence
    tab = SentencePracticeTab.__new__(SentencePracticeTab)
    tab.exercise = exercise
    tab._attempt_state = PromptAttemptState()
    tab._on_resolution = captured.append

    tab._attempt_state.mark_support("reveal")
    tab._emit_resolution("skipped", "")
    tab._emit_resolution("skipped", "")

    assert len(captured) == 1
    assert captured[0].outcome == "skipped"
    assert captured[0].support_used == frozenset({"reveal"})


def test_app_persists_focused_resolution_with_its_semantic_language() -> None:
    with TemporaryDirectory() as temp_dir:
        db = ReviewDB(Path(temp_dir) / "review.sqlite3")
        app = LangPracticeApp.__new__(LangPracticeApp)
        app.review_db = db
        app.session_id = db.start_session()
        app.session_metrics = SessionMetrics()
        app.session_footer = None
        resolution = AttemptResolution(
            language="italian", exercise_id="flashcard", skill="vocabulary",
            direction="english_to_target", item_id="ciao", outcome="correct",
            first_try=True, support_used=frozenset(), answer="ciao", first_try_correct=True,
            prompt="hello", correct_answer="ciao",
        )

        try:
            app._record_resolution(resolution)

            events = db.attempts(language="italian")
            assert len(events) == 1
            assert (events[0].skill, events[0].direction, events[0].item_id) == (
                "vocabulary", "english_to_target", "ciao",
            )
            assert db.attempts(language="french") == []
        finally:
            db.close()
