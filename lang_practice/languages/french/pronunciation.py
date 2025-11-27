"""Utilities for converting French text to IPA and learner-friendly phonetics.

The rules are intentionally lightweight and focus on core patterns from the
supporting pronunciation guide. Known vocabulary items are handled via a small
dictionary, and other words fall back to simple, rule-based approximations.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, Iterable, List, Tuple


_OVERRIDE_PRONUNCIATIONS: Dict[str, Tuple[str, str]] = {
    "bonjour": ("bɔ̃ʒuʁ", "bohng-zhoor"),
    "au": ("o", "oh"),
    "revoir": ("ʁəvwaʁ", "ruh-vwar"),
    "au revoir": ("o ʁəvwaʁ", "oh ruh-vwar"),
    "s'il": ("sil", "seel"),
    "vous": ("vu", "voo"),
    "plaît": ("plɛ", "pleh"),
    "s'il vous plaît": ("sil vu plɛ", "seel voo pleh"),
    "merci": ("mɛʁsi", "mehr-see"),
    "pardon": ("paʁdɔ̃", "par-dohn"),
    "pain": ("pɛ̃", "pan"),
    "fromage": ("fʁɔmaʒ", "fro-mahzh"),
    "eau": ("o", "oh"),
    "pomme": ("pɔm", "pom"),
    "vin": ("vɛ̃", "van"),
    "maison": ("mɛzɔ̃", "meh-zohn"),
    "chaise": ("ʃɛz", "shez"),
    "porte": ("pɔʁt", "port"),
    "fenêtre": ("fənɛtʁ", "fuh-netr"),
    "cuisine": ("kɥizin", "kwee-zeen"),
    "chat": ("ʃa", "shah"),
    "chien": ("ʃjɛ̃", "shyen"),
    "oiseau": ("wazo", "wah-zo"),
    "poisson": ("pwasɔ̃", "pwah-son"),
    "cheval": ("ʃəval", "shuh-val"),
    "je": ("ʒə", "zhuh"),
    "mange": ("mɑ̃ʒ", "mahnzh"),
    "du": ("dy", "dew"),
    "le": ("lə", "luh"),
    "est": ("ɛ", "eh"),
    "dans": ("dɑ̃", "dahn"),
    "la": ("la", "lah"),
}


_NASAL_GROUPS: Dict[str, str] = {
    "ain": "ɛ̃",
    "ein": "ɛ̃",
    "an": "ɑ̃",
    "am": "ɑ̃",
    "en": "ɑ̃",
    "em": "ɑ̃",
    "in": "ɛ̃",
    "im": "ɛ̃",
    "on": "ɔ̃",
    "om": "ɔ̃",
    "un": "œ̃",
    "um": "œ̃",
}


_DIGRAPHS: Dict[str, str] = {
    "ch": "ʃ",
    "gn": "ɲ",
    "ou": "u",
    "oi": "wa",
    "eu": "ø",
    "oeu": "ø",
    "ai": "ɛ",
    "ei": "ɛ",
    "au": "o",
    "eau": "o",
}


_SIMPLE_VOWELS: Dict[str, str] = {
    "a": "a",
    "à": "a",
    "â": "a",
    "e": "ə",
    "é": "e",
    "è": "ɛ",
    "ê": "ɛ",
    "ë": "ə",
    "i": "i",
    "î": "i",
    "ï": "i",
    "o": "ɔ",
    "ô": "o",
    "u": "y",
    "ù": "y",
    "û": "y",
    "y": "i",
}


_SIMPLE_CONSONANTS: Dict[str, str] = {
    "b": "b",
    "c": "k",
    "ç": "s",
    "d": "d",
    "f": "f",
    "g": "g",
    "h": "",
    "j": "ʒ",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "p": "p",
    "q": "k",
    "r": "ʁ",
    "s": "s",
    "t": "t",
    "v": "v",
    "w": "w",
    "x": "ks",
    "z": "z",
}


_IPA_TO_PHONETIC: Dict[str, str] = {
    "ɑ̃": "ahn",
    "ɔ̃": "ohn",
    "ɛ̃": "en",
    "œ̃": "un",
    "a": "ah",
    "e": "ay",
    "ɛ": "eh",
    "ə": "uh",
    "i": "ee",
    "o": "oh",
    "ɔ": "aw",
    "u": "oo",
    "y": "uu",
    "ø": "eu",
    "œ": "eu",
    "b": "b",
    "d": "d",
    "f": "f",
    "g": "g",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "p": "p",
    "ʁ": "r",
    "s": "s",
    "ʃ": "sh",
    "t": "t",
    "v": "v",
    "z": "z",
    "ʒ": "zh",
    "ɲ": "ny",
    "w": "w",
    "j": "y",
}

_VOWELS = set(_SIMPLE_VOWELS.keys())


def _normalize_token(token: str) -> str:
    lowered = token.lower()
    lowered = lowered.replace("’", "'").replace("�", "e")
    return lowered


def _split_words(text: str) -> Iterable[str]:
    for raw in text.split():
        core = raw.strip(".,;:!?\"'()[]«»")
        if core:
            yield core


def _rule_based_ipa_for_word(word: str) -> str:
    normalized = _normalize_token(word)

    if normalized in _OVERRIDE_PRONUNCIATIONS:
        return _OVERRIDE_PRONUNCIATIONS[normalized][0]

    ipa_parts: list[str] = []
    i = 0
    length = len(normalized)

    while i < length:
        tri = normalized[i : i + 3]
        if tri in _NASAL_GROUPS:
            next_after_tri = normalized[i + 3] if i + 3 < length else ""
            # Nasal vowels only when the following letter is not a vowel
            # and not another nasal consonant (n/m), matching guide examples
            # like \"ami\" (/ami/, not nasal) versus \"pain\" (/pɛ̃/).
            if not next_after_tri or (next_after_tri not in _VOWELS and next_after_tri not in {"n", "m"}):
                ipa_parts.append(_NASAL_GROUPS[tri])
                i += 3
                continue

        digraph = normalized[i : i + 2]
        if digraph in _NASAL_GROUPS:
            next_after_di = normalized[i + 2] if i + 2 < length else ""
            if not next_after_di or (next_after_di not in _VOWELS and next_after_di not in {"n", "m"}):
                ipa_parts.append(_NASAL_GROUPS[digraph])
                i += 2
                continue

        if digraph in _DIGRAPHS:
            ipa_parts.append(_DIGRAPHS[digraph])
            i += 2
            continue

        ch = normalized[i]
        next_ch = normalized[i + 1] if i + 1 < length else ""

        # Context-sensitive handling for C and G, following the pronunciation guide:
        # - C before e, i, y → /s/ (soft C as in "ici")
        # - C elsewhere       → /k/
        # - G before e, i, y → /ʒ/ (soft G, like French "g" in "gîte")
        # - G elsewhere       → /g/
        if ch == "c":
            ipa_parts.append("s" if next_ch in {"e", "i", "y"} else "k")
            i += 1
            continue

        if ch == "g":
            ipa_parts.append("\u0292" if next_ch in {"e", "i", "y"} else "g")
            i += 1
            continue

        if i == length - 1 and ch in {"e", "s", "t", "x", "d"}:
            i += 1
            continue

        # Prefer closed /o/ for a standalone final \"o\" (e.g., \"stylo\" → /stilo/),
        # matching the guide's rule of thumb for word-final O.
        if ch == "o":
            ipa_parts.append("o" if i == length - 1 else _SIMPLE_VOWELS[ch])
            i += 1
            continue

        if ch in _SIMPLE_VOWELS:
            ipa_parts.append(_SIMPLE_VOWELS[ch])
        elif ch in _SIMPLE_CONSONANTS:
            ipa_parts.append(_SIMPLE_CONSONANTS[ch])
        else:
            ipa_parts.append(ch)
        i += 1

    return "".join(ipa_parts)


def _phonetic_for_ipa(ipa: str) -> str:
    parts: list[str] = []
    for ch in ipa:
        mapped = _IPA_TO_PHONETIC.get(ch, "")
        if mapped:
            parts.append(mapped)
    if not parts:
        return ipa
    return "".join(parts)


@lru_cache(maxsize=512)
def to_ipa(french_text: str) -> str:
    """Convert French text to a coarse IPA transcription."""

    words = list(_split_words(french_text))
    ipa_words: list[str] = []
    for word in words:
        normalized = _normalize_token(word)
        if normalized in _OVERRIDE_PRONUNCIATIONS:
            ipa = _OVERRIDE_PRONUNCIATIONS[normalized][0]
        else:
            ipa = _rule_based_ipa_for_word(normalized)
        ipa_words.append(ipa)
    if not ipa_words:
        return ""
    return "/" + " ".join(ipa_words) + "/"


@lru_cache(maxsize=512)
def to_phonetic(french_text: str) -> str:
    """Convert French text to a learner-friendly phonetic spelling."""

    words = list(_split_words(french_text))
    phonetic_words: list[str] = []
    for word in words:
        normalized = _normalize_token(word)
        if normalized in _OVERRIDE_PRONUNCIATIONS:
            phonetic = _OVERRIDE_PRONUNCIATIONS[normalized][1]
        else:
            ipa = _rule_based_ipa_for_word(normalized)
            phonetic = _phonetic_for_ipa(ipa)
        phonetic_words.append(phonetic)
    return " ".join(phonetic_words)


def explain_pronunciation(french_text: str) -> str:
    """Return a plain-language explanation of how to say the text.

    This mirrors the pronunciation guide by:
    - showing the IPA and phonetic helper
    - calling out key sounds such as nasal vowels, the French \"r\",
      and \"zh\"/\"sh\" consonants that are not obvious from spelling.
    """

    text = french_text.strip()
    if not text:
        return "Type or select a French word or sentence to see pronunciation tips based on the guide."

    ipa = to_ipa(text)
    phonetic = to_phonetic(text)

    lines: List[str] = [f"How to say: {text}"]
    if ipa:
        lines.append(f"IPA: {ipa}")
    if phonetic:
        lines.append(f"Phonetic helper: {phonetic}")

    ipa_core = ipa.strip("/") if ipa else ""
    spelling = text.lower()
    points: List[str] = []

    # Nasal vowels: ɑ̃, ɔ̃, ɛ̃, œ̃ etc. (vowel + combining tilde)
    if "\u0303" in ipa_core:
        points.append(
            "Nasal vowels: let the sound resonate through your nose and do not fully pronounce the final 'n' or 'm'."
        )

    # French guttural R
    if "\u0281" in ipa_core:
        points.append("French 'r' (/ʁ/): a back-of-the-throat sound, not an English 'r'.")

    # /ʒ/ - the "zh" sound (e.g. in fromage)
    if "\u0292" in ipa_core:
        points.append("The /ʒ/ sound: like the 's' in English 'measure' or 'vision' (written here as 'zh').")

    # /ʃ/ - the "sh" sound (e.g. in words with 'ch')
    if "\u0283" in ipa_core:
        points.append("The /ʃ/ sound: like 'sh' in English 'she', used for many 'ch' spellings in French.")

    # French U /y/
    if "y" in ipa_core or "u" in spelling:
        points.append(
            "French 'u' (/y/): say 'ee' while rounding your lips tightly (no exact English equivalent)."
        )

    # Common vowel combinations
    if "oi" in spelling:
        points.append("The letters 'oi' sound roughly like 'wah' (as in 'moi', 'trois').")
    if "ou" in spelling:
        points.append("The letters 'ou' sound like a pure 'oo' as in 'food', without an ending glide.")
    if "eu" in spelling or "oeu" in spelling:
        points.append("The spelling 'eu'/'oeu' is a mid rounded vowel, between English 'uh' and 'er'.")

    # Highlight soft vs hard C/G from the guide.
    if "c" in spelling:
        points.append(
            "Letter 'c': before e/i/y it sounds like /s/ (soft c), otherwise like /k/ (hard c)."
        )
    if "g" in spelling:
        points.append(
            "Letter 'g': before e/i/y it sounds like /ʒ/ (soft g, 'zh'), otherwise like /g/ (hard g as in 'go')."
        )

    if not points:
        points.append(
            "This follows the regular French vowel and consonant rules from the guide: keep vowels pure and final consonants often silent."
        )

    lines.append("")  # blank line before bullets
    lines.append("Key pronunciation points:")
    lines.extend(f"- {p}" for p in points)
    return "\n".join(lines)
