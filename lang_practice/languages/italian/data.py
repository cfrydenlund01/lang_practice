"""Static data sets for the Italian language module."""

from __future__ import annotations

from typing import Sequence

from ...models import ConjugationPattern, Sentence, VocabularyItem

LANGUAGE_KEY = "italian"

ACCENTED_CHARACTERS: Sequence[str] = (
    "\u00e0",
    "\u00e8",
    "\u00e9",
    "\u00ec",
    "\u00f2",
    "\u00f3",
    "\u00f9",
)

VOCABULARY: Sequence[VocabularyItem] = (
    VocabularyItem(
        french="ciao",
        english="hello",
        category="greetings",
        part_of_speech="expression",
        tags=("greeting", "informal"),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(
        french="arrivederci",
        english="goodbye",
        category="greetings",
        part_of_speech="expression",
        tags=("greeting",),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(
        french="per favore",
        english="please",
        category="greetings",
        part_of_speech="expression",
        tags=("polite",),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(
        french="grazie",
        english="thank you",
        category="greetings",
        part_of_speech="expression",
        tags=("polite",),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(
        french="scusa",
        english="sorry",
        category="greetings",
        part_of_speech="expression",
        tags=("polite", "informal"),
        language=LANGUAGE_KEY,
    ),
    VocabularyItem(french="pane", english="bread", category="food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="formaggio", english="cheese", category="food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="acqua", english="water", category="food", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="mela", english="apple", category="food", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="vino", english="wine", category="food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="casa", english="house", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="sedia", english="chair", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="porta", english="door", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="finestra", english="window", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="cucina", english="kitchen", category="home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem(french="gatto", english="cat", category="animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="cane", english="dog", category="animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="uccello", english="bird", category="animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="pesce", english="fish", category="animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem(french="cavallo", english="horse", category="animals", gender="m", language=LANGUAGE_KEY),
)


PRESENT_TENSE: Sequence[ConjugationPattern] = (
    ConjugationPattern("parlare", "to speak", "parlo", "parli", "parla", "parliamo", "parlate", "parlano", LANGUAGE_KEY),
    ConjugationPattern("dormire", "to sleep", "dormo", "dormi", "dorme", "dormiamo", "dormite", "dormono", LANGUAGE_KEY),
    ConjugationPattern("avere", "to have", "ho", "hai", "ha", "abbiamo", "avete", "hanno", LANGUAGE_KEY),
    ConjugationPattern("essere", "to be", "sono", "sei", "\u00e8", "siamo", "siete", "sono", LANGUAGE_KEY),
    ConjugationPattern("andare", "to go", "vado", "vai", "va", "andiamo", "andate", "vanno", LANGUAGE_KEY),
)


SENTENCES: Sequence[Sentence] = (
    Sentence("greeting_ciao", "Ciao.", "Hello.", ("greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("greeting_grazie", "Grazie.", "Thank you.", ("greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_pane", "Mangio pane.", "I am eating bread.", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence(
        "home_gatto_casa",
        "Il gatto \u00e8 in casa.",
        "The cat is in the house.",
        ("home", "animals", "sentence_practice"),
        LANGUAGE_KEY,
    ),
    Sentence(
        "home_cucina",
        "La cucina \u00e8 grande.",
        "The kitchen is big.",
        ("home", "sentence_practice"),
        LANGUAGE_KEY,
    ),
)

