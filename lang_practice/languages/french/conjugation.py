"""Learner-facing present-tense conjugation lessons for French verbs."""

from __future__ import annotations

from ...models import ConjugationPattern


_IRREGULAR_LESSONS = {
    "avoir": (
        "Avoir is irregular, so do not build it from one stem. The singular forms are "
        "j’ai, tu as, and il/elle a. Nous and vous use av- (avons, avez), while "
        "ils/elles uses ont. Notice that je contracts to j’ before ai."
    ),
    "être": (
        "Être is highly irregular and its six forms must be learned as a set: je suis, "
        "tu es, il/elle est, nous sommes, vous êtes, ils/elles sont. There is no single "
        "present-tense stem to which regular endings can be added."
    ),
    "aller": (
        "Aller is irregular even though it ends in -er. The singular uses va-: je vais, "
        "tu vas, il/elle va. Nous and vous return to all- (allons, allez), but ils/elles "
        "uses vont. Learn the three stem groups: vai-/va-, all-, and vont."
    ),
}


def explain_conjugation(pattern: ConjugationPattern) -> str:
    """Explain how to form the supplied French present-tense pattern."""

    irregular = _IRREGULAR_LESSONS.get(pattern.infinitive)
    if irregular:
        return irregular

    if pattern.infinitive.endswith("er"):
        stem = pattern.infinitive[:-2]
        return (
            f"This is a regular -er verb. Remove -er to get the stem {stem}-, then add "
            "-e, -es, -e, -ons, -ez, -ent for je, tu, il/elle, nous, vous, and "
            "ils/elles. The je, il/elle, and ils/elles forms usually sound alike because "
            "their final consonants are silent."
        )

    if pattern.infinitive.endswith("ir"):
        stem = pattern.infinitive[:-2]
        return (
            f"This follows the regular finir-type -ir pattern. Remove -ir to get {stem}-, "
            "then add -is, -is, -it, -issons, -issez, -issent. The plural forms insert "
            "-iss- before their endings. Not every French -ir verb follows this pattern."
        )

    return "This verb is irregular in the present tense. Learn its six forms as a complete pattern."
