"""Shared data models used by language modules and exercises."""

from __future__ import annotations

from dataclasses import dataclass, replace
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
