"""Template-based Italian sentence generator built from the core vocabulary."""

from __future__ import annotations

from random import choice
from typing import Callable, Sequence

from ...models import Sentence, random_sentence_id
from .data import LANGUAGE_KEY

VOWEL_STARTS = (
    "a",
    "e",
    "i",
    "o",
    "u",
    "\u00e0",
    "\u00e8",
    "\u00e9",
    "\u00ec",
    "\u00f2",
    "\u00f3",
    "\u00f9",
)


def _starts_with_vowel(word: str) -> bool:
    return word.lower().startswith(tuple(VOWEL_STARTS))


def _format_article(article: str, word: str) -> str:
    if article.endswith("'"):
        return f"{article}{word}"
    return f"{article} {word}"


def _definite_article_it(gender: str | None, word: str) -> str:
    if _starts_with_vowel(word):
        return "l'"
    if gender == "f":
        return "la"
    return "il"


def _indefinite_article_it(gender: str | None) -> str:
    return "una" if gender == "f" else "un"


def _english_indef_article(word: str) -> str:
    return "an" if word.lower().startswith(("a", "e", "i", "o", "u")) else "a"


def _choose_noun(category: str | None = None):
    from ...data import vocabulary_items

    pool = vocabulary_items(part_of_speech="noun", category=category, language=LANGUAGE_KEY)
    if not pool:
        pool = vocabulary_items(part_of_speech="noun", language=LANGUAGE_KEY)
    return choice(pool)


def _sentence_io_vedo(category: str | None = None) -> Sentence:
    noun = _choose_noun(category)
    article = _definite_article_it(noun.gender, noun.french)
    italian = f"Io vedo {_format_article(article, noun.french)}."
    english = f"I see the {noun.english}."
    return Sentence(random_sentence_id("see"), italian, english, ("sentence_practice", "generated"), LANGUAGE_KEY)


def _sentence_noi_abbiamo(category: str | None = None) -> Sentence:
    noun = _choose_noun(category)
    article_it = _indefinite_article_it(noun.gender)
    article_en = _english_indef_article(noun.english)
    italian = f"Noi abbiamo {article_it} {noun.french}."
    english = f"We have {article_en} {noun.english}."
    return Sentence(random_sentence_id("have"), italian, english, ("sentence_practice", "generated"), LANGUAGE_KEY)


def _sentence_c_e(category: str | None = None) -> Sentence:
    noun = _choose_noun(category)
    article_it = _indefinite_article_it(noun.gender)
    article_en = _english_indef_article(noun.english)
    italian = f"C'\u00e8 {article_it} {noun.french} qui."
    english = f"There is {article_en} {noun.english} here."
    return Sentence(
        random_sentence_id("there_is"),
        italian,
        english,
        ("sentence_practice", "generated"),
        LANGUAGE_KEY,
    )


def _sentence_animale_casa(_: str | None = None) -> Sentence:
    animal = _choose_noun("animals")
    home = _choose_noun("home")
    italian = (
        f"{_format_article(_definite_article_it(animal.gender, animal.french), animal.french)} "
        f"\u00e8 vicino a {_format_article(_definite_article_it(home.gender, home.french), home.french)}."
    )
    english = f"The {animal.english} is near the {home.english}."
    return Sentence(random_sentence_id("animal_home"), italian, english, ("sentence_practice", "generated"), LANGUAGE_KEY)


def _sentence_cibo_casa(category: str | None = None) -> Sentence:
    food = _choose_noun(category or "food")
    place = _choose_noun("home")
    italian = (
        f"{_format_article(_definite_article_it(food.gender, food.french), food.french)} "
        f"\u00e8 in {_format_article(_definite_article_it(place.gender, place.french), place.french)}."
    )
    english = f"The {food.english} is in the {place.english}."
    return Sentence(random_sentence_id("food_home"), italian, english, ("sentence_practice", "generated"), LANGUAGE_KEY)


def _sentence_mi_piace(category: str | None = None) -> Sentence:
    noun = _choose_noun(category)
    article = _definite_article_it(noun.gender, noun.french)
    italian = f"Mi piace {_format_article(article, noun.french)}."
    english = f"I like the {noun.english}."
    return Sentence(random_sentence_id("like"), italian, english, ("sentence_practice", "generated"), LANGUAGE_KEY)


TemplateBuilder = Callable[[str | None], Sentence]

TEMPLATES: Sequence[TemplateBuilder] = (
    _sentence_io_vedo,
    _sentence_noi_abbiamo,
    _sentence_c_e,
    _sentence_animale_casa,
    _sentence_cibo_casa,
    _sentence_mi_piace,
)


def generate_sentence(category: str | None = None) -> Sentence:
    """Generate a new practice sentence using vocabulary-driven templates."""

    builder = choice(TEMPLATES)
    return builder(category)
