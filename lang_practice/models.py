"""Shared data models used by language modules and exercises."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from random import randrange
from typing import Sequence


def random_sentence_id(prefix: str = "generated") -> str:
    """Return a unique-ish identifier for generated sentences."""

    return f"{prefix}_{randrange(1_000_000)}"


@dataclass(frozen=True)
class VocabularyItem:
    """Single vocabulary entry used by flashcard-style exercises."""

    french: str
    english: str
    category: str = "general"
    gender: str | None = None
    part_of_speech: str = "noun"
    tags: Sequence[str] = ()
    language: str | None = None
    accepted_answers: Sequence[str] = ()
    id: str = ""

    @property
    def ipa(self) -> str:
        from .language_registry import get_module

        module = get_module(self.language)
        return module.to_ipa(self.french)

    @property
    def phonetic(self) -> str:
        from .language_registry import get_module

        module = get_module(self.language)
        return module.to_phonetic(self.french)

    def tagged(self, language: str) -> "VocabularyItem":
        if self.language == language:
            return self
        return replace(self, language=language)


@dataclass(frozen=True)
class ConjugationPattern:
    """Verb conjugation pattern for present tense practice."""

    infinitive: str
    english: str
    je: str
    tu: str
    il: str
    nous: str
    vous: str
    ils: str
    language: str | None = None
    id: str = ""

    def form_id(self, person: str, tense: str = "present") -> str:
        """Identify a taught form independently of the displayed pronoun or answer."""

        if not self.id:
            raise ValueError("Conjugation pattern needs an authored ID")
        if person not in {"first_singular", "second_singular", "third_singular", "first_plural", "second_plural", "third_plural"}:
            raise ValueError(f"Unknown canonical person: {person}")
        return f"{self.id}:{tense}:{person}"

    @property
    def pronouns(self) -> Sequence[str]:
        pronouns_by_language: dict[str, Sequence[str]] = {
            "french": ("je", "tu", "il/elle", "nous", "vous", "ils/elles"),
            "italian": ("io", "tu", "lui/lei", "noi", "voi", "loro"),
        }
        if self.language and self.language in pronouns_by_language:
            return pronouns_by_language[self.language]
        return pronouns_by_language["french"]

    @property
    def answers(self) -> Sequence[str]:
        return (self.je, self.tu, self.il, self.nous, self.vous, self.ils)

    def tagged(self, language: str) -> "ConjugationPattern":
        if self.language == language:
            return self
        return replace(self, language=language)


@dataclass(frozen=True)
class Sentence:
    """Sentence with translation and tags."""

    id: str
    french: str
    english: str
    tags: Sequence[str] = ()
    language: str | None = None
    accepted_answers: Sequence[str] = ()
    target_vocabulary_ids: Sequence[str] = ()
    target_verb_form_ids: Sequence[str] = ()
    taught_construction: str | None = None
    target_notes: Sequence["SentenceTargetNote"] = ()
    metadata_validated: bool = False

    @property
    def ipa(self) -> str:
        from .language_registry import get_module

        module = get_module(self.language)
        return module.to_ipa(self.french)

    @property
    def phonetic(self) -> str:
        from .language_registry import get_module

        module = get_module(self.language)
        return module.to_phonetic(self.french)

    def tagged(self, language: str) -> "Sentence":
        if self.language == language:
            return self
        return replace(self, language=language)

    @property
    def guided_ready(self) -> bool:
        """Whether authored target metadata is safe for guided selection."""

        if not self.metadata_validated or "generated" in self.tags or not self.id or not self.language:
            return False
        targets = ({("vocabulary", item_id) for item_id in self.target_vocabulary_ids}
                   | {("verb_form", item_id) for item_id in self.target_verb_form_ids})
        notes = {(note.skill, note.item_id) for note in self.target_notes}
        return bool(targets) and len(targets) == len(self.target_notes) and targets == notes and all(
            note.target_text and note.explanation and note.lesson and note.answer_cues
            for note in self.target_notes
        )


@dataclass(frozen=True)
class SentenceTargetNote:
    """Authored explanation for one sentence target.

    ``answer_cues`` are deliberately small, language-pack-owned English cues.
    They support targeted feedback without pretending to parse arbitrary
    grammar or treating every sentence target as missed.
    """

    skill: str
    item_id: str
    target_text: str
    answer_cues: Sequence[str]
    explanation: str
    lesson: str


@dataclass(frozen=True)
class AttemptEvent:
    """One resolved prompt; IDs and support describe evidence, not presentation text."""

    event_id: str
    occurred_at: datetime
    session_id: str
    language: str
    exercise_id: str
    skill: str
    direction: str
    item_id: str
    outcome: str
    first_try: bool
    support_used: frozenset[str] = frozenset()
    answer: str | None = None
    first_try_correct: bool | None = None


@dataclass(frozen=True)
class AttemptResolution:
    """A focused-practice prompt resolved by the learner.

    Tabs provide the semantic target and presentation text; the application
    supplies the session, timestamp, and durable event ID when it stores this
    resolution.  Keeping this separate from :class:`AttemptEvent` makes it
    possible to guard one displayed prompt before writing anything to SQLite.
    """

    language: str
    exercise_id: str
    skill: str
    direction: str
    item_id: str
    outcome: str
    first_try: bool
    support_used: frozenset[str]
    answer: str | None
    first_try_correct: bool | None
    prompt: str
    correct_answer: str


@dataclass(frozen=True)
class ReadinessSnapshot:
    language: str
    skill: str
    direction: str
    item_id: str
    first_try_successes: int
    first_try_attempts: int
    assisted_attempts: int
    revealed_attempts: int
    recent_misses: int
    last_attempt_at: datetime | None
    due_at: datetime | None
    unaided_success_days: int = 0
