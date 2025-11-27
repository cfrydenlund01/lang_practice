"""Base structures for pluggable language modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from ..models import ConjugationPattern, Sentence, VocabularyItem


SentenceGenerator = Callable[[str | None], Sentence]


@dataclass(frozen=True)
class LanguageModule:
    """Configuration and resources for a specific language."""

    key: str
    label: str
    tts_lang: str
    accent_characters: Sequence[str]
    vocabulary: Sequence[VocabularyItem]
    present_tense: Sequence[ConjugationPattern]
    sentences: Sequence[Sentence]
    explain_pronunciation: Callable[[str], str]
    to_ipa: Callable[[str], str]
    to_phonetic: Callable[[str], str]
    generate_sentence: SentenceGenerator
