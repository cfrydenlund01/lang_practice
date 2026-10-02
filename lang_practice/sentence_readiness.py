"""Pure sentence-readiness and authored targeted-feedback helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .exercises import normalize_answer
from .models import ReadinessSnapshot, Sentence, SentenceTargetNote


SUPPORTED = "Supported"
GUIDED = "Guided"
INDEPENDENT = "Independent"
SUPPORT_LEVELS = (SUPPORTED, GUIDED, INDEPENDENT)

TargetKey = tuple[str, str, str]


@dataclass(frozen=True)
class SessionTargetEvidence:
    """Short-lived evidence that is intentionally reset next session."""

    misses: int = 0
    help_uses: int = 0


@dataclass(frozen=True)
class SentenceReadiness:
    recommended_level: str
    presentation_level: str
    reason: str


@dataclass(frozen=True)
class SentenceFeedback:
    message: str
    lesson: str
    target_key: TargetKey | None


def sentence_target_keys(sentence: Sentence) -> tuple[TargetKey, ...]:
    """Return the durable evidence keys explicitly authored on a sentence."""

    keys = [
        ("vocabulary", "target_to_english", item_id)
        for item_id in sentence.target_vocabulary_ids
    ]
    keys.extend(
        ("verb_form", "target_form", item_id)
        for item_id in sentence.target_verb_form_ids
    )
    return tuple(keys)


def recommend_sentence_support(
    sentence: Sentence,
    snapshots: Mapping[TargetKey, ReadinessSnapshot],
    session_evidence: Mapping[TargetKey, SessionTargetEvidence] | None = None,
    user_selected_level: str | None = None,
) -> SentenceReadiness:
    """Recommend support from durable evidence and this session's context.

    The recommendation never locks presentation.  Passing a user-selected
    level changes ``presentation_level`` while preserving the recommendation
    and its learner-readable reason.
    """

    if not sentence.guided_ready:
        raise ValueError("Sentence does not have validated guided-readiness metadata")
    if user_selected_level is not None and user_selected_level not in SUPPORT_LEVELS:
        raise ValueError(f"Unknown sentence support level: {user_selected_level}")

    keys = sentence_target_keys(sentence)
    session_evidence = session_evidence or {}
    same_session_misses = sum(session_evidence.get(key, SessionTargetEvidence()).misses for key in keys)
    same_session_help = sum(session_evidence.get(key, SessionTargetEvidence()).help_uses for key in keys)

    known = [snapshots[key] for key in keys if key in snapshots]
    unknown_count = len(keys) - len(known) + sum(snapshot.first_try_attempts == 0 for snapshot in known)
    strong = [
        snapshot
        for snapshot in known
        if snapshot.first_try_attempts >= 3
        and snapshot.first_try_successes / snapshot.first_try_attempts >= 0.8
        and snapshot.unaided_success_days >= 2
        and snapshot.recent_misses == 0
    ]

    if same_session_misses or same_session_help:
        recommendation = SUPPORTED
        reason = "Extra support is recommended because this session included a miss or help on a core target."
    elif not keys or unknown_count:
        recommendation = SUPPORTED
        reason = "Extra support is recommended because at least one core target is still unfamiliar."
    elif len(strong) == len(keys):
        recommendation = INDEPENDENT
        reason = "Independent practice is recommended because every core target has unaided success across days."
    else:
        recommendation = GUIDED
        reason = "Guided practice is recommended because the core targets have mixed or still-developing evidence."

    return SentenceReadiness(
        recommended_level=recommendation,
        presentation_level=user_selected_level or recommendation,
        reason=reason,
    )


def targeted_sentence_feedback(
    sentence: Sentence,
    answer: str,
    snapshots: Mapping[TargetKey, ReadinessSnapshot] | None = None,
) -> SentenceFeedback:
    """Choose one authored target for useful feedback on a missed sentence.

    Missing authored English cues identify a likely target.  When all cues are
    present, persistent evidence chooses one developing target.  This is not a
    grammar parser and never labels the sentence's other targets as failures.
    """

    if not sentence.guided_ready or not sentence.target_notes:
        return SentenceFeedback(
            "Not quite. Compare your answer with the authored translation; no individual word has been marked wrong.",
            sentence.taught_construction or "",
            None,
        )

    normalized_answer = normalize_answer(answer)
    missing = [note for note in sentence.target_notes if not _contains_any_cue(normalized_answer, note.answer_cues)]
    candidates = missing or list(sentence.target_notes)
    snapshots = snapshots or {}
    note = min(candidates, key=lambda candidate: _target_strength(candidate, snapshots))
    key = _note_key(note)
    construction = f" {sentence.taught_construction}" if sentence.taught_construction else ""
    message = (
        f"Focus on {note.target_text}: {note.explanation} "
        "The other sentence elements have not been marked wrong."
        f"{construction}"
    )
    return SentenceFeedback(message, note.lesson, key)


def support_scaffold(sentence: Sentence, level: str) -> str:
    """Return authored, level-appropriate scaffolding without parsing text."""

    if level not in SUPPORT_LEVELS:
        raise ValueError(f"Unknown sentence support level: {level}")
    if level == INDEPENDENT:
        return "No scaffold shown; Hint remains available."

    construction = sentence.taught_construction or "Use the sentence's familiar words and form."
    targets = ", ".join(note.target_text for note in sentence.target_notes)
    if level == GUIDED:
        return f"Construction: {construction} Core targets: {targets}."
    explanations = "; ".join(f"{note.target_text}: {note.explanation}" for note in sentence.target_notes)
    return f"Construction: {construction} Support: {explanations}"


def _contains_any_cue(normalized_answer: str, cues: Sequence[str]) -> bool:
    padded = f" {normalized_answer} "
    return any(f" {normalize_answer(cue)} " in padded for cue in cues if normalize_answer(cue))


def _note_key(note: SentenceTargetNote) -> TargetKey:
    direction = "target_to_english" if note.skill == "vocabulary" else "target_form"
    return note.skill, direction, note.item_id


def _target_strength(
    note: SentenceTargetNote,
    snapshots: Mapping[TargetKey, ReadinessSnapshot],
) -> tuple[float, int]:
    snapshot = snapshots.get(_note_key(note))
    if snapshot is None or snapshot.first_try_attempts == 0:
        return (0.0, 0)
    return (snapshot.first_try_successes / snapshot.first_try_attempts, snapshot.first_try_attempts)
