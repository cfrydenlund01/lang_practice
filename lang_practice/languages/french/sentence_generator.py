"""Template-based French sentence generator built from the core vocabulary."""

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
    "y",
    "h",
    "\u00e0",
    "\u00e2",
    "\u00e4",
    "\u00e9",
    "\u00e8",
    "\u00ea",
    "\u00eb",
    "\u00ee",
    "\u00ef",
    "\u00f4",
    "\u00f6",
    "\u00f9",
    "\u00fb",
    "\u0153",
)


def _starts_with_vowel(word: str) -> bool:
    return word.lower().startswith(tuple(VOWEL_STARTS))


def _format_article(article: str, word: str) -> str:
    if article.endswith("'"):
        return f"{article}{word}"
    return f"{article} {word}"


def _definite_article_fr(gender: str | None, word: str) -> str:
    if _starts_with_vowel(word):
        return "l'"
    if gender == "f":
        return "la"
    return "le"


def _indefinite_article_fr(gender: str | None) -> str:
    return "une" if gender == "f" else "un"


def _english_indef_article(word: str) -> str:
    return "an" if word.lower().startswith(("a", "e", "i", "o", "u")) else "a"


def _choose_noun(category: str | None = None):
    from ...data import vocabulary_items

    pool = vocabulary_items(part_of_speech="noun", category=category)
    if not pool:
        pool = vocabulary_items(part_of_speech="noun")
    return choice(pool)


def _sentence_je_vois(category: str | None = None) -> Sentence:
    noun = _choose_noun(category)
    article = _definite_article_fr(noun.gender, noun.french)
    french = f"Je vois {_format_article(article, noun.french)}."
    english = f"I see the {noun.english}."
    return Sentence(
        random_sentence_id("see"), french, english, ("sentence_practice", "generated"), LANGUAGE_KEY
    )


def _sentence_nous_avons(category: str | None = None) -> Sentence:
    noun = _choose_noun(category)
    article_fr = _indefinite_article_fr(noun.gender)
    article_en = _english_indef_article(noun.english)
    french = f"Nous avons {article_fr} {noun.french}."
    english = f"We have {article_en} {noun.english}."
    return Sentence(
        random_sentence_id("have"), french, english, ("sentence_practice", "generated"), LANGUAGE_KEY
    )


def _sentence_il_y_a(category: str | None = None) -> Sentence:
    noun = _choose_noun(category)
    article_fr = _indefinite_article_fr(noun.gender)
    article_en = _english_indef_article(noun.english)
    french = f"Il y a {article_fr} {noun.french} ici."
    english = f"There is {article_en} {noun.english} here."
    return Sentence(
        random_sentence_id("there_is"), french, english, ("sentence_practice", "generated"), LANGUAGE_KEY
    )


def _sentence_animal_home(_: str | None = None) -> Sentence:
    animal = _choose_noun("animals")
    home = _choose_noun("home")
    french = (
        f"{_format_article(_definite_article_fr(animal.gender, animal.french), animal.french)} "
        f"est pr\u00e8s de {_format_article(_definite_article_fr(home.gender, home.french), home.french)}."
    )
    english = f"The {animal.english} is near the {home.english}."
    return Sentence(
        random_sentence_id("animal_home"), french, english, ("sentence_practice", "generated"), LANGUAGE_KEY
    )


def _sentence_food_home(category: str | None = None) -> Sentence:
    food = _choose_noun(category or "food")
    place = _choose_noun("home")
    french = (
        f"{_format_article(_definite_article_fr(food.gender, food.french), food.french)} "
        f"est dans {_format_article(_definite_article_fr(place.gender, place.french), place.french)}."
    )
    english = f"The {food.english} is in the {place.english}."
    return Sentence(
        random_sentence_id("food_home"), french, english, ("sentence_practice", "generated"), LANGUAGE_KEY
    )


def _sentence_j_aime(category: str | None = None) -> Sentence:
    noun = _choose_noun(category)
    article = _definite_article_fr(noun.gender, noun.french)
    french = f"J'aime {_format_article(article, noun.french)}."
    english = f"I like the {noun.english}."
    return Sentence(
        random_sentence_id("like"), french, english, ("sentence_practice", "generated"), LANGUAGE_KEY
    )


TemplateBuilder = Callable[[str | None], Sentence]

TEMPLATES: Sequence[TemplateBuilder] = (
    _sentence_je_vois,
    _sentence_nous_avons,
    _sentence_il_y_a,
    _sentence_animal_home,
    _sentence_food_home,
    _sentence_j_aime,
)


def generate_sentence(category: str | None = None) -> Sentence:
    """Generate a new practice sentence using vocabulary-driven templates."""

    builder = choice(TEMPLATES)
    return builder(category)
