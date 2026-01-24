"""Utilities for converting Italian text to IPA and learner-friendly phonetics.

The rules are intentionally lightweight and mirror the bundled pronunciation
guide (Standard Central Italian). Known vocabulary items are handled via a small
dictionary, and other words fall back to simple, rule-based approximations.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, Iterable, List, Tuple

_OVERRIDE_PRONUNCIATIONS: Dict[str, Tuple[str, str]] = {
    "ciao": ("tʃao", "chow"),
    "arrivederci": ("arri.veˈdɛrtʃi", "ah-ree-veh-DEHR-chee"),
    "per": ("per", "pehr"),
    "favore": ("faˈvoːre", "fa-VOH-reh"),
    "per favore": ("per faˈvoːre", "pehr fa-VOH-reh"),
    "grazie": ("ˈɡratːsje", "GRAHT-tsyeh"),
    "scusa": ("ˈskuːza", "SKOO-za"),
    "pane": ("ˈpaːne", "PAH-neh"),
    "formaggio": ("forˈmadːʒo", "for-MAHD-joh"),
    "acqua": ("ˈakːwa", "AHK-kwah"),
    "mela": ("ˈmeːla", "MAY-la"),
    "vino": ("ˈviːno", "VEE-no"),
    "casa": ("ˈkaːsa", "KAH-sa"),
    "sedia": ("ˈsɛːdja", "SEH-dya"),
    "porta": ("ˈpɔrta", "POR-ta"),
    "finestra": ("fiˈnɛstra", "fee-NES-tra"),
    "cucina": ("kuˈtʃiːna", "koo-CHEE-na"),
    "gatto": ("ˈɡatːto", "GAHT-to"),
    "cane": ("ˈkaːne", "KAH-neh"),
    "uccello": ("utˈtʃɛlːlo", "oot-CHEL-lo"),
    "pesce": ("ˈpeʃe", "PEH-sheh"),
    "cavallo": ("kaˈvalːlo", "ka-VAHL-lo"),
    "io": ("io", "ee-oh"),
    "tu": ("tu", "too"),
    "lui": ("lui", "loo-ee"),
    "lei": ("lɛi", "leh-ee"),
    "noi": ("noi", "noy"),
    "voi": ("voi", "voy"),
    "loro": ("ˈloːro", "LOH-ro"),
    "il": ("il", "eel"),
    "la": ("la", "lah"),
    "un": ("un", "oon"),
    "una": ("ˈuːna", "OO-na"),
    "in": ("in", "een"),
    "è": ("ɛ", "eh"),
}

_VOWELS = set("aeiouàèéìòóù")

_VOWEL_IPA: Dict[str, str] = {
    "a": "a",
    "à": "a",
    "e": "e",
    "é": "e",
    "è": "ɛ",
    "i": "i",
    "ì": "i",
    "o": "o",
    "ó": "o",
    "ò": "ɔ",
    "u": "u",
    "ù": "u",
}

_CONSONANT_IPA: Dict[str, str] = {
    "b": "b",
    "d": "d",
    "f": "f",
    "h": "",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "p": "p",
    "q": "k",
    "r": "r",
    "t": "t",
    "v": "v",
    "x": "ks",
}


def _normalize_token(token: str) -> str:
    lowered = token.lower()
    return lowered.replace("’", "'")


def _split_words(text: str) -> Iterable[str]:
    for raw in text.split():
        core = raw.strip(".,;:!?\"'()[]«»")
        if core:
            yield core


def _is_vowel(ch: str) -> bool:
    return ch in _VOWELS


def _rule_based_ipa_for_word(word: str) -> str:
    normalized = _normalize_token(word)
    if normalized in _OVERRIDE_PRONUNCIATIONS:
        return _OVERRIDE_PRONUNCIATIONS[normalized][0]

    parts: list[str] = []
    i = 0
    length = len(normalized)

    while i < length:
        ch = normalized[i]

        if ch == "'":
            i += 1
            continue

        if normalized.startswith("sch", i):
            parts.append("sk")
            i += 3
            continue

        if normalized.startswith("qu", i):
            parts.append("kw")
            i += 2
            continue

        if normalized.startswith("gn", i):
            parts.append("ɲ")
            i += 2
            continue

        if normalized.startswith("gli", i):
            after = normalized[i + 3] if i + 3 < length else ""
            if not after:
                parts.append("ʎi")
                i += 3
                continue
            if _is_vowel(after):
                parts.append("ʎ" + _VOWEL_IPA.get(after, after))
                i += 4
                continue

        if normalized.startswith("sc", i) and i + 2 < length and normalized[i + 2] in {"e", "i", "è", "é"}:
            parts.append("ʃ")
            i += 2
            continue

        if normalized.startswith("ch", i):
            parts.append("k")
            i += 2
            continue

        if normalized.startswith("gh", i):
            parts.append("g")
            i += 2
            continue

        if normalized.startswith("ci", i):
            after = normalized[i + 2] if i + 2 < length else ""
            if after and _is_vowel(after):
                parts.append("tʃ" + _VOWEL_IPA.get(after, after))
                i += 3
                continue

        if normalized.startswith("gi", i):
            after = normalized[i + 2] if i + 2 < length else ""
            if after and _is_vowel(after):
                parts.append("dʒ" + _VOWEL_IPA.get(after, after))
                i += 3
                continue

        if normalized.startswith(("ce", "cè", "cé"), i):
            vowel = normalized[i + 1]
            parts.append("tʃ" + _VOWEL_IPA.get(vowel, vowel))
            i += 2
            continue

        if normalized.startswith(("ge", "gè", "gé"), i):
            vowel = normalized[i + 1]
            parts.append("dʒ" + _VOWEL_IPA.get(vowel, vowel))
            i += 2
            continue

        if i + 1 < length and normalized[i + 1] == ch and ch.isalpha() and not _is_vowel(ch):
            next_after = normalized[i + 2] if i + 2 < length else ""
            if ch == "c":
                parts.append("tʃː" if next_after in {"e", "i", "è", "é"} else "kː")
            elif ch == "g":
                parts.append("dʒː" if next_after in {"e", "i", "è", "é"} else "gː")
            elif ch == "s":
                parts.append("sː")
            elif ch == "z":
                parts.append("tsː")
            elif ch == "r":
                parts.append("rː")
            else:
                parts.append((_CONSONANT_IPA.get(ch) or ch) + "ː")
            i += 2
            continue

        if ch == "c":
            nxt = normalized[i + 1] if i + 1 < length else ""
            parts.append("tʃ" if nxt in {"e", "i", "è", "é"} else "k")
            i += 1
            continue

        if ch == "g":
            nxt = normalized[i + 1] if i + 1 < length else ""
            parts.append("dʒ" if nxt in {"e", "i", "è", "é"} else "g")
            i += 1
            continue

        if ch == "s":
            prev = normalized[i - 1] if i > 0 else ""
            nxt = normalized[i + 1] if i + 1 < length else ""
            parts.append("z" if prev and nxt and _is_vowel(prev) and _is_vowel(nxt) else "s")
            i += 1
            continue

        if ch == "z":
            parts.append("ts")
            i += 1
            continue

        if ch in {"i", "u"}:
            nxt = normalized[i + 1] if i + 1 < length else ""
            prev = normalized[i - 1] if i > 0 else ""
            if prev and not _is_vowel(prev) and nxt and _is_vowel(nxt):
                parts.append("j" if ch == "i" else "w")
                i += 1
                continue

        if ch in _VOWEL_IPA:
            parts.append(_VOWEL_IPA[ch])
        elif ch in _CONSONANT_IPA:
            parts.append(_CONSONANT_IPA[ch])
        elif ch.isalpha():
            parts.append(ch)
        i += 1

    return "".join(parts)


def _phonetic_for_ipa(ipa: str) -> str:
    simplified = ipa.replace("ː", "")
    simplified = simplified.replace("tʃ", "ch").replace("dʒ", "j")

    mapping = {
        "a": "ah",
        "e": "eh",
        "ɛ": "eh",
        "i": "ee",
        "o": "oh",
        "ɔ": "aw",
        "u": "oo",
        "b": "b",
        "d": "d",
        "f": "f",
        "g": "g",
        "k": "k",
        "l": "l",
        "m": "m",
        "n": "n",
        "p": "p",
        "r": "r",
        "s": "s",
        "z": "z",
        "v": "v",
        "ʃ": "sh",
        "ʎ": "ly",
        "ɲ": "ny",
        "j": "y",
        "w": "w",
    }

    out: list[str] = []
    i = 0
    while i < len(simplified):
        chunk = simplified[i : i + 2]
        if chunk in {"ch", "sh", "ny", "ly", "ts", "dz"}:
            out.append(chunk)
            i += 2
            continue
        out.append(mapping.get(simplified[i], ""))
        i += 1

    rendered = "".join(out)
    return rendered or ipa


@lru_cache(maxsize=512)
def to_ipa(italian_text: str) -> str:
    """Convert Italian text to a coarse IPA transcription."""

    words = list(_split_words(italian_text))
    ipa_words: list[str] = []
    for word in words:
        normalized = _normalize_token(word)
        ipa_words.append(_rule_based_ipa_for_word(normalized))
    if not ipa_words:
        return ""
    return "/" + " ".join(ipa_words) + "/"


@lru_cache(maxsize=512)
def to_phonetic(italian_text: str) -> str:
    """Convert Italian text to a learner-friendly phonetic spelling."""

    words = list(_split_words(italian_text))
    phonetic_words: list[str] = []
    for word in words:
        normalized = _normalize_token(word)
        if normalized in _OVERRIDE_PRONUNCIATIONS:
            phonetic = _OVERRIDE_PRONUNCIATIONS[normalized][1]
        else:
            phonetic = _phonetic_for_ipa(_rule_based_ipa_for_word(normalized))
        phonetic_words.append(phonetic)
    return " ".join(phonetic_words)


def explain_pronunciation(italian_text: str) -> str:
    """Return a plain-language explanation of how to say the text."""

    text = italian_text.strip()
    if not text:
        return "Type or select an Italian word or sentence to see pronunciation tips based on the guide."

    ipa = to_ipa(text)
    phonetic = to_phonetic(text)

    lines: List[str] = [f"How to say: {text}"]
    if ipa:
        lines.append(f"IPA: {ipa}")
    if phonetic:
        lines.append(f"Phonetic helper: {phonetic}")

    spelling = text.lower()
    ipa_core = ipa.strip("/") if ipa else ""
    points: List[str] = []

    if "gli" in spelling:
        points.append("'gli' before a vowel is the palatal /ʎ/ sound (similar to the 'lli' in 'million').")
    if "gn" in spelling or "ɲ" in ipa_core:
        points.append("'gn' is /ɲ/ (like Spanish ñ), not a hard 'g' + 'n'.")
    if "sc" in spelling:
        points.append("'sc' before e/i is /ʃ/ ('sh'); otherwise it stays /sk/.")
    if "c" in spelling:
        points.append("'c' is /tʃ/ before e/i and /k/ elsewhere; 'ch' keeps it hard before e/i.")
    if "g" in spelling:
        points.append("'g' is /dʒ/ before e/i and /g/ elsewhere; 'gh' keeps it hard before e/i.")
    if "ː" in ipa_core or any(double in spelling for double in ("bb", "cc", "dd", "ff", "gg", "ll", "mm", "nn", "pp", "rr", "ss", "tt", "zz")):
        points.append("Double consonants are held longer (they matter for meaning), e.g. gatto vs. gato.")
    if any(ch in spelling for ch in ("à", "è", "é", "ì", "ò", "ó", "ù")):
        points.append("Written accents mark stress and can signal open/closed e/o (è/é, ò/ó).")

    if not points:
        points.append("Italian is very phonetic: pronounce each written vowel clearly and avoid English-style schwa reductions.")

    lines.append("")
    lines.append("Key pronunciation points:")
    lines.extend(f"- {p}" for p in points)
    return "\n".join(lines)

