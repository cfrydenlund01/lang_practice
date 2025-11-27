"""Static data sets for the French language module."""

from __future__ import annotations

from typing import Sequence

from ...models import ConjugationPattern, Sentence, VocabularyItem

LANGUAGE_KEY = "french"

ACCENTED_CHARACTERS: Sequence[str] = (
    "\u00e0",
    "\u00e2",
    "\u00e4",
    "\u00e7",
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
)

VOCABULARY: Sequence[VocabularyItem] = (
    VocabularyItem(
        french="bonjour",
        english="hello",
        category="greetings",
        part_of_speech="expression",
        tags=("greeting",),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(
        french="au revoir",
        english="goodbye",
        category="greetings",
        part_of_speech="expression",
        tags=("greeting",),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(
        french="s'il vous pla\u00eet",
        english="please",
        category="greetings",
        part_of_speech="expression",
        tags=("polite",),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(
        french="merci",
        english="thank you",
        category="greetings",
        part_of_speech="expression",
        tags=("polite",),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(
        french="pardon",
        english="sorry",
        category="greetings",
        part_of_speech="expression",
        tags=("polite",),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(french="pain", english="bread", category="food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="fromage", english="cheese", category="food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="eau", english="water", category="food", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="pomme", english="apple", category="food", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="vin", english="wine", category="food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="maison", english="house", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="chaise", english="chair", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="porte", english="door", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="fen\u00eatre", english="window", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="cuisine", english="kitchen", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="chat", english="cat", category="animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="chien", english="dog", category="animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="oiseau", english="bird", category="animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="poisson", english="fish", category="animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="cheval", english="horse", category="animals", gender="m", language=LANGUAGE_KEY),
)


PRESENT_TENSE: Sequence[ConjugationPattern] = (
    ConjugationPattern("parler", "to speak", "parle", "parles", "parle", "parlons", "parlez", "parlent", LANGUAGE_KEY),
    ConjugationPattern("finir", "to finish", "finis", "finis", "finit", "finissons", "finissez", "finissent", LANGUAGE_KEY),
    ConjugationPattern("avoir", "to have", "ai", "as", "a", "avons", "avez", "ont", LANGUAGE_KEY),
    ConjugationPattern("\u00eatre", "to be", "suis", "es", "est", "sommes", "\u00eates", "sont", LANGUAGE_KEY),
    ConjugationPattern("aller", "to go", "vais", "vas", "va", "allons", "allez", "vont", LANGUAGE_KEY),
)


SENTENCES: Sequence[Sentence] = (
    Sentence("greeting_bonjour", "Bonjour.", "Hello.", ("greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("greeting_merci", "Merci.", "Thank you.", ("greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_pain", "Je mange du pain.", "I am eating bread.", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence(
        "home_chat_maison",
        "Le chat est dans la maison.",
        "The cat is in the house.",
        ("home", "animals", "sentence_practice"),
        LANGUAGE_KEY,
    ),
)
