from __future__ import annotations

from datetime import datetime, timezone

import pytest

from lang_practice.data import guided_sentences
from lang_practice.exercises import PromptAttemptState, answer_matches
from lang_practice.gui import SentencePracticeTab
from lang_practice.language_registry import get_module
from lang_practice.models import ReadinessSnapshot, Sentence
from lang_practice.sentence_readiness import (
    GUIDED,
    INDEPENDENT,
    SUPPORTED,
    SessionTargetEvidence,
    recommend_sentence_support,
    sentence_target_keys,
    targeted_sentence_feedback,
)


def _snapshot(
    language: str,
    key: tuple[str, str, str],
    *,
    successes: int,
    attempts: int,
    misses: int = 0,
    assisted: int = 0,
    success_days: int = 2,
) -> ReadinessSnapshot:
    return ReadinessSnapshot(
        language=language,
        skill=key[0],
        direction=key[1],
        item_id=key[2],
        first_try_successes=successes,
        first_try_attempts=attempts,
        assisted_attempts=assisted,
        revealed_attempts=0,
        recent_misses=misses,
        last_attempt_at=datetime(2026, 9, 28, tzinfo=timezone.utc),
        due_at=None,
        unaided_success_days=success_days,
    )


def _sentence(language: str, sentence_id: str) -> Sentence:
    return next(sentence for sentence in guided_sentences(language) if sentence.id == sentence_id)


def test_unknown_target_recommends_supported() -> None:
    sentence = _sentence("french", "greeting_bonjour")
    assert recommend_sentence_support(sentence, {}).recommended_level == SUPPORTED


def test_mixed_strong_and_weak_targets_recommend_guided() -> None:
    sentence = _sentence("french", "home_chat_maison")
    keys = sentence_target_keys(sentence)
    snapshots = {
        keys[0]: _snapshot("french", keys[0], successes=4, attempts=4),
        keys[1]: _snapshot("french", keys[1], successes=1, attempts=2),
        keys[2]: _snapshot("french", keys[2], successes=3, attempts=3),
    }
    assert recommend_sentence_support(sentence, snapshots).recommended_level == GUIDED


def test_same_session_miss_temporarily_adds_support_then_resets_next_session() -> None:
    sentence = _sentence("italian", "food_pane")
    keys = sentence_target_keys(sentence)
    snapshots = {key: _snapshot("italian", key, successes=4, attempts=4) for key in keys}

    during_session = recommend_sentence_support(
        sentence,
        snapshots,
        {keys[0]: SessionTargetEvidence(misses=1)},
    )
    later_session = recommend_sentence_support(sentence, snapshots, {})

    assert during_session.recommended_level == SUPPORTED
    assert later_session.recommended_level == INDEPENDENT


def test_hinted_target_is_supported_and_durable_recent_miss_is_guided() -> None:
    sentence = _sentence("italian", "food_pane")
    keys = sentence_target_keys(sentence)
    strong = {key: _snapshot("italian", key, successes=4, attempts=4) for key in keys}
    with_hint = recommend_sentence_support(
        sentence,
        strong,
        {keys[1]: SessionTargetEvidence(help_uses=1)},
    )
    after_return = dict(strong)
    after_return[keys[1]] = _snapshot("italian", keys[1], successes=4, attempts=5, misses=1, assisted=1)

    assert with_hint.recommended_level == SUPPORTED
    assert recommend_sentence_support(sentence, after_return).recommended_level == GUIDED

    hinted_only = {keys[0]: _snapshot("italian", keys[0], successes=0, attempts=0, assisted=1)}
    assert recommend_sentence_support(sentence, hinted_only).recommended_level == SUPPORTED


def test_user_selected_support_changes_presentation_not_recommendation() -> None:
    sentence = _sentence("french", "greeting_bonjour")
    result = recommend_sentence_support(sentence, {}, user_selected_level=INDEPENDENT)

    assert result.recommended_level == SUPPORTED
    assert result.presentation_level == INDEPENDENT


def test_one_day_of_repeated_success_does_not_imply_independent_readiness() -> None:
    sentence = _sentence("italian", "food_pane")
    snapshots = {
        key: _snapshot("italian", key, successes=4, attempts=4, success_days=1)
        for key in sentence_target_keys(sentence)
    }
    assert recommend_sentence_support(sentence, snapshots).recommended_level == GUIDED


def test_visible_scaffold_marks_the_sentence_answer_as_helped() -> None:
    class _Var:
        def __init__(self, value: str = "") -> None:
            self.value = value

        def get(self) -> str:
            return self.value

        def set(self, value: str) -> None:
            self.value = value

    tab = SentencePracticeTab.__new__(SentencePracticeTab)
    tab._readiness_provider = lambda sentence: {}
    tab._session_target_evidence = {}
    tab._attempt_state = PromptAttemptState()
    tab._current_snapshots = {}
    tab.support_choice_var = _Var("Recommended")
    tab.readiness_var = _Var()
    tab.scaffold_var = _Var()

    tab._refresh_readiness(_sentence("french", "greeting_bonjour"))

    assert tab._attempt_state.support_used == {"hint"}


def test_targeted_feedback_names_only_the_missing_authored_target() -> None:
    sentence = _sentence("italian", "food_pane")
    feedback = targeted_sentence_feedback(sentence, "I am eating rice")

    assert feedback.target_key == ("vocabulary", "target_to_english", "pane")
    assert "pane" in feedback.message
    assert "other sentence elements have not been marked wrong" in feedback.message.lower()
    assert "Vocabulary lesson" in feedback.lesson


def test_targeted_feedback_can_offer_a_verb_form_lesson() -> None:
    sentence = _sentence("italian", "food_pane")
    feedback = targeted_sentence_feedback(sentence, "Bread")

    assert feedback.target_key == ("verb_form", "target_form", "mangiare:present:first_singular")
    assert "mangio" in feedback.message
    assert "Verb lesson" in feedback.lesson


@pytest.mark.parametrize("language", ["french", "italian"])
def test_curated_metadata_references_authored_language_targets(language: str) -> None:
    module = get_module(language)
    vocabulary_ids = {item.id for item in module.vocabulary}
    people = (
        "first_singular", "second_singular", "third_singular",
        "first_plural", "second_plural", "third_plural",
    )
    form_ids = {pattern.form_id(person) for pattern in module.present_tense for person in people}

    for sentence in guided_sentences(language):
        note_keys = {(note.skill, note.item_id) for note in sentence.target_notes}
        assert set(sentence.target_vocabulary_ids) <= vocabulary_ids
        assert set(sentence.target_verb_form_ids) <= form_ids
        assert all(("vocabulary", item_id) in note_keys for item_id in sentence.target_vocabulary_ids)
        assert all(("verb_form", item_id) in note_keys for item_id in sentence.target_verb_form_ids)


@pytest.mark.parametrize(
    ("language", "sentence_id", "answer"),
    [
        ("french", "home_chat_maison", "The cat is inside the house."),
        ("italian", "food_pane", "I eat bread."),
    ],
)
def test_complete_curated_path_exists_in_each_language(language: str, sentence_id: str, answer: str) -> None:
    sentence = _sentence(language, sentence_id)

    assert sentence.guided_ready
    assert sentence.target_notes
    assert sentence.accepted_answers
    assert answer_matches(answer, sentence.english, sentence.accepted_answers)
    assert targeted_sentence_feedback(sentence, answer).target_key is not None


def test_generated_or_untagged_sentence_cannot_enter_guided_readiness() -> None:
    generated = Sentence("generated_1", "Bonjour.", "Hello.", tags=("generated",), language="french")
    with pytest.raises(ValueError, match="validated"):
        recommend_sentence_support(generated, {})


def test_validation_flag_alone_does_not_admit_unmapped_sentence() -> None:
    malformed = Sentence("bad", "Bonjour.", "Hello.", language="french", metadata_validated=True)
    assert not malformed.guided_ready
