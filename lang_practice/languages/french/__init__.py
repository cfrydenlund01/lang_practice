"""French language module wiring."""

from __future__ import annotations

from ..base import LanguageModule
from .data import ACCENTED_CHARACTERS, LANGUAGE_KEY, PRESENT_TENSE, SENTENCES, VOCABULARY
from .pronunciation import explain_pronunciation, to_ipa, to_phonetic
from .sentence_generator import generate_sentence

MODULE = LanguageModule(
    key=LANGUAGE_KEY,
    label="French",
    tts_lang="fr",
    accent_characters=ACCENTED_CHARACTERS,
    vocabulary=VOCABULARY,
    present_tense=PRESENT_TENSE,
    sentences=SENTENCES,
    explain_pronunciation=explain_pronunciation,
    to_ipa=to_ipa,
    to_phonetic=to_phonetic,
    generate_sentence=generate_sentence,
)

__all__ = ["MODULE"]
