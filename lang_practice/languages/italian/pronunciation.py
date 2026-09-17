"""Standard-Italian pronunciation and learner respelling.

The implementation follows the bundled Markdown pronunciation guide.  It is
lexicon-first for facts that spelling does not reliably encode (stress,
open/closed e and o, s/z, affricates, and hiatus), with a conservative
spelling-rule fallback for unfamiliar words.
"""

from __future__ import annotations

from functools import lru_cache
import re
from typing import Iterable, List, Sequence


# Syllable dots are retained internally and in displayed IPA because they make
# stress, hiatus, and consonant length much clearer to a learner.
_LEXICON_IPA: dict[str, str] = {
    # Guide examples and high-frequency function words.
    "a": "a",
    "abbiamo": "abˈbja.mo",
    "ai": "ai",
    "al": "al",
    "alla": "ˈal.la",
    "alle": "ˈal.le",
    "c'è": "tʃɛ",
    "che": "ke",
    "chi": "ki",
    "ciao": "ˈtʃao",
    "come": "ˈko.me",
    "cosa": "ˈkɔ.za",
    "cuore": "ˈkwɔ.re",
    "dell'acqua": "delˈlak.kwa",
    "dov'è": "doˈvɛ",
    "dove": "ˈdo.ve",
    "e": "e",
    "è": "ɛ",
    "gli": "ʎi",
    "idea": "iˈdɛ.a",
    "il": "il",
    "in": "in",
    "io": "ˈi.o",
    "la": "la",
    "lo": "lo",
    "lei": "lɛi",
    "loro": "ˈlo.ro",
    "luna": "ˈlu.na",
    "l'albergo": "lalˈbɛr.go",
    "l'ufficio": "lufˈfi.tʃo",
    "mi": "mi",
    "mai": "mai",
    "noi": "noi",
    "non": "non",
    "per": "per",
    "piano": "ˈpja.no",
    "più": "pju",
    "poi": "pɔi",
    "può": "pwɔ",
    "tu": "tu",
    "un": "un",
    "un'allergia": "unal.lerˈdʒi.a",
    "una": "ˈu.na",
    "uomo": "ˈwɔ.mo",
    "vedo": "ˈve.do",
    "voi": "voi",

    # Greetings and social language.
    "arrivederci": "ar.ri.veˈdɛr.tʃi",
    "buonasera": "bwo.naˈse.ra",
    "buongiorno": "bwonˈdʒor.no",
    "conoscerti": "koˈnoʃ.ʃer.ti",
    "fantastico": "fanˈta.sti.ko",
    "favore": "faˈvo.re",
    "grazie": "ˈgrat.tsje",
    "piacere": "pjaˈtʃe.re",
    "piace": "ˈpja.tʃe",
    "presto": "ˈprɛ.sto",
    "prego": "ˈprɛ.go",
    "scusa": "ˈsku.za",
    "scusi": "ˈsku.zi",
    "sbaglio": "ˈzbaʎ.ʎo",
    "schema": "ˈske.ma",
    "schiena": "ˈskjɛ.na",
    "sciarpa": "ˈʃar.pa",
    "sciocco": "ˈʃɔk.ko",
    "sveglia": "ˈzvɛʎ.ʎa",

    # Food and home.
    "acqua": "ˈak.kwa",
    "casa": "ˈka.za",
    "appartamento": "ap.par.taˈmen.to",
    "bagno": "ˈbaɲ.ɲo",
    "caffè": "kafˈfɛ",
    "cena": "ˈtʃe.na",
    "chiave": "ˈkja.ve",
    "colazione": "ko.latˈtsjo.ne",
    "conto": "ˈkon.to",
    "cucina": "kuˈtʃi.na",
    "finestra": "fiˈnɛ.stra",
    "formaggio": "forˈmad.dʒo",
    "mela": "ˈme.la",
    "mangio": "ˈman.dʒo",
    "mappa": "ˈmap.pa",
    "pane": "ˈpa.ne",
    "porta": "ˈpɔr.ta",
    "pranzo": "ˈpran.dzo",
    "sedia": "ˈsɛ.dja",
    "stanza": "ˈstan.tsa",
    "tè": "tɛ",
    "vegetariano": "ve.dʒe.taˈrja.no",

    # People and animals.
    "amica": "aˈmi.ka",
    "amico": "aˈmi.ko",
    "bambina": "bamˈbi.na",
    "bambino": "bamˈbi.no",
    "bello": "ˈbɛl.lo",
    "cane": "ˈka.ne",
    "cavallo": "kaˈval.lo",
    "famiglia": "faˈmiʎ.ʎa",
    "figlio": "ˈfiʎ.ʎo",
    "gatto": "ˈgat.to",
    "gnocchi": "ˈɲɔk.ki",
    "glicine": "ˈgli.tʃi.ne",
    "insegnante": "in.seɲˈɲan.te",
    "ogni": "ˈoɲ.ɲi",
    "paese": "paˈe.ze",
    "persona": "perˈso.na",
    "pesce": "ˈpeʃ.ʃe",
    "uccello": "utˈtʃɛl.lo",

    # Travel, city, directions, and time.
    "aeroporto": "a.e.roˈpɔr.to",
    "albergo": "alˈbɛr.go",
    "biglietto": "biʎˈʎɛt.to",
    "destra": "ˈdɛ.stra",
    "domani": "doˈma.ni",
    "farmacia": "far.maˈtʃi.a",
    "giorno": "ˈdʒor.no",
    "giri": "ˈdʒi.ri",
    "ieri": "ˈjɛ.ri",
    "lontano": "lonˈta.no",
    "mattina": "matˈti.na",
    "museo": "muˈzɛ.o",
    "oggi": "ˈɔd.dʒi",
    "nove": "ˈnɔ.ve",
    "ora": "ˈo.ra",
    "ospedale": "o.speˈda.le",
    "piazza": "ˈpjat.tsa",
    "prenotazione": "pre.no.tatˈtsjo.ne",
    "roma": "ˈro.ma",
    "sera": "ˈse.ra",
    "sinistra": "siˈni.stra",
    "stazione": "statˈtsjo.ne",
    "strada": "ˈstra.da",
    "treno": "ˈtrɛ.no",
    "valigia": "vaˈli.dʒa",
    "vicino": "viˈtʃi.no",

    # Learning, work, descriptions, and feelings.
    "felice": "feˈli.tʃe",
    "grande": "ˈgran.de",
    "italiano": "i.taˈlja.no",
    "lavoro": "laˈvo.ro",
    "lingua": "ˈliŋ.gwa",
    "piccolo": "ˈpik.ko.lo",
    "preoccupato": "pre.ok.kuˈpa.to",
    "riunione": "ri.uˈnjo.ne",
    "scuola": "ˈskwɔ.la",
    "stanco": "ˈstan.ko",
    "studente": "stuˈdɛn.te",
    "ufficio": "ufˈfi.tʃo",

    # Infinitives whose stress or sound pattern deserves an explicit entry.
    "avere": "aˈve.re",
    "andare": "anˈda.re",
    "bere": "ˈbe.re",
    "capire": "kaˈpi.re",
    "dovere": "doˈve.re",
    "dormire": "dorˈmi.re",
    "essere": "ˈɛs.se.re",
    "fare": "ˈfa.re",
    "mangiare": "manˈdʒa.re",
    "parlare": "parˈla.re",
    "potere": "poˈte.re",
    "prendere": "ˈprɛn.de.re",
    "sapere": "saˈpe.re",
    "sciare": "ʃiˈa.re",
    "studiare": "stuˈdja.re",
    "uscire": "uʃˈʃi.re",
    "venire": "veˈni.re",
    "volere": "voˈle.re",

    # Common sentence forms and guide regression examples.
    "aiutarmi": "a.juˈtar.mi",
    "aiuto": "aˈju.to",
    "allergia": "al.lerˈdʒi.a",
    "andiamo": "anˈdja.mo",
    "bisogno": "biˈzoɲ.ɲo",
    "capisco": "kaˈpi.sko",
    "chiuso": "ˈkju.zo",
    "dopo": "ˈdo.po",
    "lentamente": "len.taˈmen.te",
    "mia": "ˈmi.a",
    "molto": "ˈmol.to",
    "noci": "ˈno.tʃi",
    "otto": "ˈɔt.to",
    "posso": "ˈpɔs.so",
    "ripetere": "riˈpɛ.te.re",
    "sono": "ˈso.no",
    "spiaggia": "ˈspjad.dʒa",
    "studio": "ˈstu.djo",
    "tavolo": "ˈta.vo.lo",
    "telefono": "teˈlɛ.fo.no",
    "vespa": "ˈvɛs.pa",
    "vorrei": "vorˈrɛi",
    "voglio": "ˈvɔʎ.ʎo",
    "zero": "ˈdzɛ.ro",
    "zio": "ˈtsi.o",
    # Remaining common function and corpus words.
    "da": "da",
    "di": "di",
    "ho": "o",
    "l'appartamento": "lap.par.taˈmen.to",
    "libro": "ˈli.bro",
    "parla": "ˈpar.la",
    "parte": "ˈpar.te",
    "qui": "kwi",
    "va": "va",
    "vino": "ˈvi.no",
}

_HELPER_OVERRIDES: dict[str, str] = {
    # Validated examples from the guide. These prioritize readability where a
    # mechanical phoneme-by-phoneme rendering would obscure syllable timing.
    "bello": "BÈL-loh",
    "caffè": "kahf-FÈ",
    "cane": "KAH-né",
    "ciao": "CHOW",
    "famiglia": "fah-MEE-lyah",
    "gli": "lyee",
    "gnocchi": "NYÒK-kee",
    "mela": "MÉ-lah",
    "perché": "pehr-KÉ",
    "pesce": "PÉSH-sheh",
    "sciare": "shee-AH-ré",
    "spiaggia": "SPYAH-jah",
    "stazione": "staht-TSYÓ-neh",
    "vespa": "VÈS-pah",
}

_ORTHOGRAPHIC_VOWELS = set("aeiouàèéìòóù")
_IPA_VOWELS = {"a", "e", "ɛ", "i", "o", "ɔ", "u"}
_ACCENTED_VOWELS = set("àèéìòóù")
_FRONT_VOWELS = set("eièéì")

_VOWEL_IPA = {
    "a": "a", "à": "a",
    "e": "e", "é": "e", "è": "ɛ",
    "i": "i", "ì": "i",
    "o": "o", "ó": "o", "ò": "ɔ",
    "u": "u", "ù": "u",
}

_SIMPLE_CONSONANTS = {
    "b": "b", "d": "d", "f": "f", "k": "k", "l": "l",
    "m": "m", "n": "n", "p": "p", "r": "r", "t": "t",
    "v": "v",
}

_VOICED_AFTER_S = set("bdgvlmnr")
_VALID_SECOND_ONSET = {"r", "l"}
_VALID_FIRST_ONSET = {"p", "b", "t", "d", "k", "g", "f", "v", "tʃ", "dʒ"}


def _normalize_token(token: str) -> str:
    return token.casefold().replace("’", "'")


def _split_words(text: str) -> Iterable[str]:
    """Yield words while retaining internal apostrophes and written accents."""

    yield from re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:['’][A-Za-zÀ-ÖØ-öø-ÿ]+)*", text)


def _is_orthographic_vowel(ch: str) -> bool:
    return ch in _ORTHOGRAPHIC_VOWELS


def _is_intervocalic(word: str, start: int, width: int = 1) -> bool:
    before = word[start - 1] if start > 0 else ""
    after_index = start + width
    after = word[after_index] if after_index < len(word) else ""
    return _is_orthographic_vowel(before) and _is_orthographic_vowel(after)


def _graphemes_to_tokens(word: str) -> list[str]:
    """Convert predictable Italian spelling patterns to broad IPA tokens."""

    tokens: list[str] = []
    i = 0
    while i < len(word):
        ch = word[i]
        following = word[i + 1] if i + 1 < len(word) else ""
        after_two = word[i + 2] if i + 2 < len(word) else ""

        if ch == "'":
            i += 1
            continue

        if word.startswith("sch", i):
            tokens.extend(("s", "k"))
            i += 3
            continue
        if word.startswith("qu", i):
            tokens.extend(("k", "w"))
            i += 2
            continue
        if word.startswith("gn", i):
            tokens.append("ɲ")
            if _is_intervocalic(word, i, 2):
                tokens.append("ɲ")
            i += 2
            continue
        if word.startswith("gli", i):
            after = word[i + 3] if i + 3 < len(word) else ""
            if after and _is_orthographic_vowel(after):
                if i > 0:
                    tokens.append("ʎ")
                tokens.extend(("ʎ", _VOWEL_IPA[after]))
                i += 4
                continue
            if not after:
                tokens.extend(("ʎ", "i"))
                i += 3
                continue

        # Soft sc, including the usually diacritic i in scia/scio/sciu.
        if word.startswith("sc", i) and after_two in _FRONT_VOWELS:
            sound = ["ʃ", "ʃ"] if _is_intervocalic(word, i, 2) else ["ʃ"]
            if after_two in {"i", "ì"} and i + 3 < len(word) and _is_orthographic_vowel(word[i + 3]):
                sound.append(_VOWEL_IPA[word[i + 3]])
                i += 4
            else:
                i += 2
            tokens.extend(sound)
            continue

        if word.startswith("ch", i):
            tokens.append("k")
            i += 2
            continue
        if word.startswith("gh", i):
            tokens.append("g")
            i += 2
            continue

        # Written double c/g before a front vowel is a long affricate.
        if word.startswith("cc", i) or word.startswith("gg", i):
            letter = ch
            front = after_two in _FRONT_VOWELS
            sound = ("tʃ" if letter == "c" else "dʒ") if front else ("k" if letter == "c" else "g")
            tokens.extend((sound, sound))
            i += 2
            if front and i < len(word) and word[i] in {"i", "ì"} and i + 1 < len(word) and _is_orthographic_vowel(word[i + 1]):
                tokens.append(_VOWEL_IPA[word[i + 1]])
                i += 2
            continue

        # Diacritic i after c/g before another vowel.
        if ch in {"c", "g"} and following in {"i", "ì"} and after_two and _is_orthographic_vowel(after_two):
            tokens.extend((("tʃ" if ch == "c" else "dʒ"), _VOWEL_IPA[after_two]))
            i += 3
            continue

        if ch in {"c", "g"}:
            if following in _FRONT_VOWELS:
                tokens.append("tʃ" if ch == "c" else "dʒ")
            else:
                tokens.append("k" if ch == "c" else "g")
            i += 1
            continue

        if i + 1 < len(word) and following == ch and ch.isalpha() and not _is_orthographic_vowel(ch):
            if ch == "s":
                sound = "s"
            elif ch == "z":
                sound = "ts"
            else:
                sound = _SIMPLE_CONSONANTS.get(ch, ch)
            tokens.extend((sound, sound))
            i += 2
            continue

        if ch == "s":
            previous = word[i - 1] if i > 0 else ""
            if following in _VOICED_AFTER_S:
                tokens.append("z")
            elif _is_orthographic_vowel(previous) and _is_orthographic_vowel(following):
                tokens.append("z")
            else:
                tokens.append("s")
            i += 1
            continue
        if ch == "z":
            tokens.append("ts")
            i += 1
            continue

        if ch in {"i", "u"} and ch not in _ACCENTED_VOWELS:
            previous = word[i - 1] if i > 0 else ""
            if previous and not _is_orthographic_vowel(previous) and following and _is_orthographic_vowel(following):
                tokens.append("j" if ch == "i" else "w")
                i += 1
                continue

        if ch == "n" and following:
            if following in {"p", "b", "m"}:
                tokens.append("m")
                i += 1
                continue
            if following in {"q", "k"} or (following in {"c", "g"} and after_two not in _FRONT_VOWELS):
                tokens.append("ŋ")
                i += 1
                continue

        if ch in _VOWEL_IPA:
            tokens.append(_VOWEL_IPA[ch])
        elif ch in _SIMPLE_CONSONANTS:
            tokens.append(_SIMPLE_CONSONANTS[ch])
        elif ch == "h":
            pass
        elif ch == "x":
            tokens.extend(("k", "s"))
        elif ch == "q":
            tokens.append("k")
        elif ch.isalpha():
            tokens.append(ch)
        i += 1
    return tokens


def _nuclei(tokens: Sequence[str]) -> list[tuple[int, int]]:
    """Return contiguous vowel ranges; remaining hiatuses live in the lexicon."""

    result: list[tuple[int, int]] = []
    i = 0
    while i < len(tokens):
        if tokens[i] not in _IPA_VOWELS:
            i += 1
            continue
        start = i
        while i + 1 < len(tokens) and tokens[i + 1] in _IPA_VOWELS:
            i += 1
        result.append((start, i + 1))
        i += 1
    return result


def _onset_length(cluster: Sequence[str]) -> int:
    if not cluster:
        return 0
    if len(cluster) >= 2 and cluster[-2] in _VALID_FIRST_ONSET and cluster[-1] in _VALID_SECOND_ONSET:
        onset = 2
    else:
        onset = 1
    if len(cluster) > onset and cluster[-onset - 1] == "s":
        onset += 1
    return onset


def _syllabify(tokens: Sequence[str]) -> list[list[str]]:
    nuclei = _nuclei(tokens)
    if not nuclei:
        return [list(tokens)] if tokens else []
    boundaries = [0]
    for index in range(len(nuclei) - 1):
        cluster_start = nuclei[index][1]
        next_nucleus = nuclei[index + 1][0]
        cluster = tokens[cluster_start:next_nucleus]
        boundaries.append(next_nucleus - _onset_length(cluster))
    boundaries.append(len(tokens))
    return [list(tokens[boundaries[i]:boundaries[i + 1]]) for i in range(len(boundaries) - 1)]


def _rule_based_ipa_for_word(word: str) -> str:
    normalized = _normalize_token(word)
    if normalized in _LEXICON_IPA:
        return _LEXICON_IPA[normalized]

    tokens = _graphemes_to_tokens(normalized)
    syllables = _syllabify(tokens)
    if not syllables:
        return ""
    stress_index = len(syllables) - 1 if any(ch in _ACCENTED_VOWELS for ch in normalized) else max(0, len(syllables) - 2)
    rendered: list[str] = []
    for index, syllable in enumerate(syllables):
        prefix = "ˈ" if index == stress_index and len(syllables) > 1 else ""
        rendered.append(prefix + "".join(syllable))
    return ".".join(rendered)


_HELPER_TOKEN_MAP = {
    "tʃ": "ch", "dʒ": "j", "ts": "ts", "dz": "dz",
    "a": "ah", "e": "é", "ɛ": "è", "i": "ee", "o": "ó", "ɔ": "ò", "u": "oo",
    "b": "b", "d": "d", "f": "f", "g": "g", "k": "k", "l": "l", "m": "m",
    "n": "n", "ŋ": "ng", "p": "p", "r": "r", "s": "s", "z": "z", "t": "t", "v": "v",
    "ʃ": "sh", "ʎ": "ly", "ɲ": "ny", "j": "y", "w": "w",
}
_IPA_MULTI_TOKENS = ("tʃ", "dʒ", "ts", "dz")


def _ipa_units(ipa_syllable: str) -> list[str]:
    units: list[str] = []
    i = 0
    while i < len(ipa_syllable):
        matched = next((token for token in _IPA_MULTI_TOKENS if ipa_syllable.startswith(token, i)), None)
        if matched:
            units.append(matched)
            i += len(matched)
        elif ipa_syllable[i] not in {"ˈ", "ː"}:
            units.append(ipa_syllable[i])
            i += 1
        else:
            i += 1
    return units


def _phonetic_for_ipa(ipa: str) -> str:
    rendered: list[str] = []
    # Lexical IPA follows standard notation and may place the stress marker
    # directly after a coda consonant.  Split there for learner syllabification.
    syllabified = re.sub(r"(?<!^)(?<!\.)ˈ", ".ˈ", ipa)
    for raw_syllable in syllabified.split("."):
        stressed = raw_syllable.startswith("ˈ")
        helper = "".join(_HELPER_TOKEN_MAP.get(unit, unit) for unit in _ipa_units(raw_syllable))
        rendered.append(helper.upper() if stressed else helper)
    return "-".join(part for part in rendered if part)


def _ipa_for_word(word: str) -> str:
    normalized = _normalize_token(word)
    return _LEXICON_IPA.get(normalized, _rule_based_ipa_for_word(normalized))


def _helper_for_word(word: str) -> str:
    normalized = _normalize_token(word)
    return _HELPER_OVERRIDES.get(normalized, _phonetic_for_ipa(_ipa_for_word(normalized)))


@lru_cache(maxsize=1024)
def to_ipa(italian_text: str) -> str:
    """Return broad, syllabified IPA for Italian text."""

    words = list(_split_words(italian_text))
    pronunciations = [_ipa_for_word(word) for word in words]
    return f"/{' '.join(pronunciations)}/" if pronunciations else ""


@lru_cache(maxsize=1024)
def to_phonetic(italian_text: str) -> str:
    """Return the guide-defined learner respelling for Italian text."""

    return " ".join(_helper_for_word(word) for word in _split_words(italian_text))


def _uncertainty_points(words: Sequence[str]) -> list[str]:
    points: list[str] = []
    unknown = [_normalize_token(word) for word in words if _normalize_token(word) not in _LEXICON_IPA]
    if not unknown:
        return points
    if any(not any(ch in _ACCENTED_VOWELS for ch in word) and sum(_is_orthographic_vowel(ch) for ch in word) > 1 for word in unknown):
        points.append("Unlisted words use a penultimate-stress fallback; verify lexical stress in DOP or Treccani.")
    if any("e" in word or "o" in word for word in unknown):
        points.append("Unmarked e/o quality is estimated as closed in unlisted words.")
    if any("z" in word or re.search(r"[aeiou]s[aeiou]", word) for word in unknown):
        points.append("The s/z value is lexical in this word and may require a dictionary entry.")
    if any(re.search(r"[aeiou]{2}", word) for word in unknown):
        points.append("Adjacent vowels may form a glide, diphthong, or hiatus; the fallback is approximate.")
    return points


def explain_pronunciation(italian_text: str) -> str:
    """Explain a pronunciation using the corrected Italian guide."""

    text = italian_text.strip()
    if not text:
        return "Select Italian text to see IPA, stress, syllables, and pronunciation guidance."

    words = list(_split_words(text))
    ipa = to_ipa(text)
    helper = to_phonetic(text)
    spelling = " ".join(_normalize_token(word) for word in words)
    ipa_core = ipa.strip("/")
    points: List[str] = []

    if "gli" in spelling or "ʎ" in ipa_core:
        points.append("gli before another vowel usually represents long palatal /ʎʎ/; final gli also has /i/.")
    if "gn" in spelling or "ɲ" in ipa_core:
        points.append("gn is palatal /ɲ/, made with the middle of the tongue toward the hard palate.")
    if "sc" in spelling:
        points.append("sc is /ʃ/ before e/i and /sk/ elsewhere; sciare is the lexical /ʃiˈare/ exception.")
    if "c" in spelling:
        points.append("c is /tʃ/ before e/i and /k/ elsewhere; ch keeps /k/ before e/i.")
    if "g" in spelling:
        points.append("g is /dʒ/ before e/i and /g/ elsewhere; gh keeps /g/ before e/i.")
    if any(double in spelling for double in ("bb", "cc", "dd", "ff", "gg", "ll", "mm", "nn", "pp", "rr", "ss", "tt", "zz")) or any(sound in ipa_core for sound in ("ʃ.ʃ", "ɲ.ɲ", "ʎ.ʎ")):
        points.append("The repeated consonant crosses a syllable boundary and must be held longer.")
    if any(ch in spelling for ch in _ACCENTED_VOWELS):
        points.append("A written accent marks stress; è/ò are open vowels and é/ó are closed vowels.")
    points.extend(_uncertainty_points(words))
    if not points:
        points.append("Keep every vowel clear; capital letters in the helper mark the stressed syllable.")

    lines = [f"How to say: {text}", f"IPA: {ipa}", f"Phonetic helper: {helper}", "", "Key pronunciation points:"]
    lines.extend(f"- {point}" for point in points)
    return "\n".join(lines)
