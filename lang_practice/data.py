"""Helpers that expose the active language module's data."""

from __future__ import annotations

from random import choice
from typing import Iterable, List, Sequence

from .language_registry import get_module
from .models import ConjugationPattern, Sentence, VocabularyItem


def accented_characters(language: str | None = None) -> Sequence[str]:
    module = get_module(language)
    return tuple(module.accent_characters)


def categories(items: Iterable[VocabularyItem]) -> List[str]:
    """Return the unique category names in the provided sequence."""

    seen: List[str] = []
    for item in items:
        if item.category not in seen:
            seen.append(item.category)
    return seen


def vocabulary_items(
    part_of_speech: str | None = None,
    category: str | None = None,
    *,
    language: str | None = None,
) -> List[VocabularyItem]:
    """Return filtered vocabulary items for downstream components."""

    module = get_module(language)
    items = list(module.vocabulary)
    if category and category != "all":
        items = [item for item in items if item.category == category]
    if part_of_speech:
        items = [item for item in items if item.part_of_speech == part_of_speech]
    return items


def random_vocabulary_item(
    category: str | None = None,
    *,
    part_of_speech: str | None = None,
    language: str | None = None,
) -> VocabularyItem:
    """Return a vocabulary item, optionally filtered by category and part of speech."""

    pool = vocabulary_items(part_of_speech=part_of_speech, category=category, language=language)
    if not pool:
        pool = list(get_module(language).vocabulary)
    return choice(pool)


def present_tense_patterns(language: str | None = None) -> Sequence[ConjugationPattern]:
    module = get_module(language)
    return module.present_tense


def random_conjugation_pattern(language: str | None = None) -> ConjugationPattern:
    """Select a random conjugation pattern."""

    return choice(present_tense_patterns(language))


def sentences(language: str | None = None) -> Sequence[Sentence]:
    module = get_module(language)
    return module.sentences
