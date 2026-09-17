"""Learner-facing present-tense conjugation lessons for Italian verbs."""

from __future__ import annotations

from dataclasses import dataclass

from ...models import ConjugationPattern


@dataclass(frozen=True)
class _Lesson:
    big_idea: str
    build: str
    notice: str
    practice: str


_SPECIAL_LESSONS = {
    "mangiare": _Lesson(
        "Mangiare is a regular -are verb with a spelling adjustment, not a new set of endings.",
        "Start with mangi-. Add the usual -are endings. When the ending begins with i, the two i's "
        "share one written i: mangi + i -> mangi and mangi + iamo -> mangiamo.",
        "The i before a or o keeps g soft, as in mangia and mangio. Think 'protect the soft g,' not "
        "'add an extra syllable.'",
        "Cover the table and build noi: mangi- + -iamo. Then use the same spelling idea for tu.",
    ),
    "studiare": _Lesson(
        "Studiare uses the normal -are pattern; its stem simply already ends in i.",
        "Remove -are to get studi-. Add -o, -i, -a, -iamo, -ate, -ano. Where stem and ending meet "
        "at i, write one i: studi and studiamo, never studii or studiiamo.",
        "Nothing irregular happens to the sound or meaning. This is just Italian avoiding a doubled i.",
        "Build tu and noi from studi-. Say the stem first, then attach the ending without doubling i.",
    ),
    "capire": _Lesson(
        "Capire belongs to the -ire family that expands the stem with -isc- in four subject forms.",
        "Use capisc- with io, tu, lui/lei, and loro; use the shorter cap- with noi and voi. The endings "
        "themselves are the familiar -ire endings.",
        "Visualize a 'boot' around the conjugation table: the four outside forms take -isc-, while noi "
        "and voi inside the gap do not. Compare capisco with capiamo.",
        "Before answering, ask: 'Is this noi or voi?' If yes, use cap-. Otherwise begin with capisc-.",
    ),
    "avere": _Lesson(
        "Avere is irregular, but its forms contain useful spelling and grouping clues.",
        "The singular and loro forms use a silent h: ho, hai, ha, hanno. Noi and voi return to the "
        "recognizable av- family: abbiamo and avete.",
        "The h is not pronounced; it distinguishes these forms from common words such as o ('or') and "
        "a ('to'). Pair io with ho and lui/lei with ha; then notice hanno echoes ha with nn.",
        "Reconstruct the two plural anchors first: noi abbiamo, voi avete. Then choose the h-form for the subject.",
    ),
    "essere": _Lesson(
        "Essere is highly irregular, so learn it through relationships instead of six isolated items.",
        "Group the forms as io/loro sono, tu sei, lui/lei è, and the rhyming plural pair noi siamo / "
        "voi siete.",
        "Io and loro share sono. The accent on è matters: e means 'and,' while è means 'is.' The s- "
        "at the start of sono, sei, siamo, and siete gives the family a sound anchor.",
        "Name the subject group before the form: shared sono, singular partner, or siamo/siete plural pair.",
    ),
    "andare": _Lesson(
        "Andare alternates between a short va-/vad- family and the visible infinitive stem and-.",
        "Use and- for noi and voi: andiamo, andate. Around those two anchors, use vado, vai, va, "
        "and vanno for io, tu, lui/lei, and loro.",
        "This is another useful 'boot' pattern: noi and voi preserve and-, while the four surrounding "
        "forms shorten to v-. Loro vanno doubles n.",
        "Check the subject first. If it is noi or voi, keep and-. Otherwise start by recalling va.",
    ),
    "fare": _Lesson(
        "Fare has three visible stem shapes, but subjects organize them into small, predictable groups.",
        "Io and noi use facc- (faccio, facciamo); tu, lui/lei, and voi use fa- (fai, fa, fate); loro "
        "uses the doubled form fanno.",
        "Link io with noi through facc-. Link the three middle fa- forms by their shared opening. Then "
        "treat fanno as fa + the strong loro sound -nno.",
        "Sort the subject into facc-, fa-, or fanno before adding or recalling the rest of the form.",
    ),
    "venire": _Lesson(
        "Venire changes its stem in the singular and loro, while noi and voi remain regular anchors.",
        "Use veng- for io and loro, vien- for tu and lui/lei, and plain ven- for noi and voi. This gives "
        "vengo/vengono, vieni/viene, and veniamo/venite.",
        "The subject pairs are the shortcut: io+loro, tu+lui/lei, noi+voi. You only need to choose "
        "among veng-, vien-, and ven-.",
        "For the prompt, identify its paired subject first; retrieve that pair's stem, then its ending.",
    ),
    "bere": _Lesson(
        "Bere looks short and irregular, but its present tense behaves regularly once you find the hidden stem bev-.",
        "Use bev- and attach the ordinary -ere endings: -o, -i, -e, -iamo, -ete, -ono.",
        "The v comes from the older form bevere and appears in every present-tense form. So do not build "
        "from be-; make bev- your starting point.",
        "Say bev- first, then choose the ending from the subject. For noi, that produces bev- + -iamo.",
    ),
    "uscire": _Lesson(
        "Uscire uses one stem inside the noi/voi pair and another around it.",
        "Use usc- for noi and voi: usciamo, uscite. Use esc- for io, tu, lui/lei, and loro: esco, esci, "
        "esce, escono.",
        "Use the same 'boot' picture as capire and andare: noi and voi keep what you see in the infinitive; "
        "the four outside forms change to esc-.",
        "Ask whether the subject is noi or voi. That single decision tells you usc- versus esc-.",
    ),
    "sapere": _Lesson(
        "Sapere has several stem shapes, but the plural forms reveal memorable sound patterns.",
        "The singular runs so, sai, sa. Then use sapp- for noi (sappiamo), regular-looking sap- for voi "
        "(sapete), and sann- for loro (sanno).",
        "Notice the consonant strengthening: pp in sappiamo and nn in sanno. Also pair sai and sa as the "
        "related tu and lui/lei forms.",
        "Build by subject group: singular so/sai/sa, then the plural anchors sappiamo, sapete, sanno.",
    ),
    "potere": _Lesson(
        "Potere alternates among poss-, puo-, and pot-, with subject groups telling you which one to use.",
        "Use poss- for io, noi, and loro; puo- for tu and lui/lei; and pot- for voi. The resulting groups "
        "are posso/possiamo/possono, puoi/può, and potete.",
        "Think 3-2-1: three poss- subjects, two puo- subjects, one pot- subject. Keep the written accent "
        "in può ('he/she can').",
        "Classify the subject as 3, 2, or 1 before recalling the form; this turns six answers into three patterns.",
    ),
    "volere": _Lesson(
        "Volere is easier as three subject groups than as a six-item list.",
        "Use vogli- with io, noi, and loro; vuo- with tu and lui/lei; and vol- with voi. These lead to "
        "voglio/vogliamo/vogliono, vuoi/vuole, and volete.",
        "It has the same 3-2-1 grouping as potere: three vogli- subjects, two vuo- subjects, and one vol- "
        "subject. Voi is the form that looks most like the infinitive.",
        "Identify the group first. If the prompt is voi, the visible vol- stem gives you the answer quickly.",
    ),
    "dovere": _Lesson(
        "Dovere is best learned as a mostly dev- pattern with two plural checkpoints.",
        "Use dev- for io, tu, lui/lei, and loro. Noi strengthens to dobb- in dobbiamo, while voi keeps "
        "the infinitive-like dov- in dovete.",
        "Do not treat all plural subjects alike: noi doubles b, voi preserves dov-, and loro returns to "
        "dev-. The contrast dobbiamo / dovete / devono is the key pattern.",
        "Check for noi or voi first. If neither appears, start from dev- and attach the matching ending.",
    ),
}


_REGULAR_ENDINGS = {
    "are": ("-o, -i, -a, -iamo, -ate, -ano", "-a", "-ate", "-ano"),
    "ere": ("-o, -i, -e, -iamo, -ete, -ono", "-e", "-ete", "-ono"),
    "ire": ("-o, -i, -e, -iamo, -ite, -ono", "-e", "-ite", "-ono"),
}


def _format_lesson(pattern: ConjugationPattern, lesson: _Lesson) -> str:
    meaning = pattern.english.removeprefix("to ")
    return (
        f"{pattern.infinitive} — to {meaning}\n\n"
        f"BIG IDEA\n{lesson.big_idea}\n\n"
        f"BUILD THE FORM\n{lesson.build}\n\n"
        f"PATTERN TO NOTICE\n{lesson.notice}\n\n"
        f"TRY THIS METHOD\n{lesson.practice}"
    )


def _regular_lesson(pattern: ConjugationPattern, family: str) -> _Lesson:
    endings, third_singular, voi_ending, loro_ending = _REGULAR_ENDINGS[family]
    stem = pattern.infinitive[: -len(family)]
    return _Lesson(
        f"This is a regular -{family} verb. You can generate every form from one stem and one reusable ending pattern.",
        f"Remove -{family} to reveal {stem}-. Then attach {endings} in the order io, tu, lui/lei, "
        "noi, voi, loro.",
        f"Across all three regular families, io ends in -o, tu in -i, and noi in -iamo. For -{family}, "
        f"the family markers are lui/lei {third_singular}, voi {voi_ending}, and loro {loro_ending}.",
        f"Say the subject, keep the stem {stem}-, and choose only its ending. For noi, for example, "
        f"{stem}- + -iamo gives {pattern.nous}.",
    )


def explain_conjugation(pattern: ConjugationPattern) -> str:
    """Return a short lesson that teaches how to reconstruct an Italian form."""

    lesson = _SPECIAL_LESSONS.get(pattern.infinitive)
    if lesson is not None:
        return _format_lesson(pattern, lesson)

    for family in _REGULAR_ENDINGS:
        if pattern.infinitive.endswith(family):
            return _format_lesson(pattern, _regular_lesson(pattern, family))

    return _format_lesson(
        pattern,
        _Lesson(
            "This present-tense pattern does not fit one of the three regular families.",
            "Look for forms that share a stem or sound, then group their subjects together.",
            "No reliable regular rule is available for this entry, so smaller subject groups will be "
            "more useful than six disconnected answers.",
            "Cover the table, recall one subject group, and check it before moving to the next group.",
        ),
    )
