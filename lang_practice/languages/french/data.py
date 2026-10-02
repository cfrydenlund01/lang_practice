"""Static data sets for the French language module."""

from __future__ import annotations

from typing import Sequence

from ...models import ConjugationPattern, Sentence, SentenceTargetNote, VocabularyItem

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
        id="bonjour",
    ),
    VocabularyItem(
        french="au revoir",
        english="goodbye",
        category="greetings",
        part_of_speech="expression",
        tags=("greeting",),
        language=LANGUAGE_KEY,
        id="au_revoir",
    ),
    VocabularyItem(
        french="s'il vous pla\u00eet",
        english="please",
        category="greetings",
        part_of_speech="expression",
        tags=("polite",),
        language=LANGUAGE_KEY,
        id="s_il_vous_plait",
    ),
    VocabularyItem(
        french="merci",
        english="thank you",
        category="greetings",
        part_of_speech="expression",
        tags=("polite",),
        language=LANGUAGE_KEY,
        id="merci",
    ),
    VocabularyItem(
        french="pardon",
        english="sorry",
        category="greetings",
        part_of_speech="expression",
        tags=("polite",),
        language=LANGUAGE_KEY,
        id="pardon",
    ),
    VocabularyItem(french="pain", english="bread", category="food", gender="m", language=LANGUAGE_KEY, id="pain"),
    VocabularyItem(french="fromage", english="cheese", category="food", gender="m", language=LANGUAGE_KEY, id="fromage"),
    VocabularyItem(french="eau", english="water", category="food", gender="f", language=LANGUAGE_KEY, id="eau"),
    VocabularyItem(french="pomme", english="apple", category="food", gender="f", language=LANGUAGE_KEY, id="pomme"),
    VocabularyItem(french="vin", english="wine", category="food", gender="m", language=LANGUAGE_KEY, id="vin"),
    VocabularyItem(french="maison", english="house", category="home", gender="f", language=LANGUAGE_KEY, id="maison"),
    VocabularyItem(french="chaise", english="chair", category="home", gender="f", language=LANGUAGE_KEY, id="chaise"),
    VocabularyItem(french="porte", english="door", category="home", gender="f", language=LANGUAGE_KEY, id="porte"),
    VocabularyItem(french="fen\u00eatre", english="window", category="home", gender="f", language=LANGUAGE_KEY, id="fenetre"),
    VocabularyItem(french="cuisine", english="kitchen", category="home", gender="f", language=LANGUAGE_KEY, id="cuisine"),
    VocabularyItem(french="chat", english="cat", category="animals", gender="m", language=LANGUAGE_KEY, id="chat"),
    VocabularyItem(french="chien", english="dog", category="animals", gender="m", language=LANGUAGE_KEY, id="chien"),
    VocabularyItem(french="oiseau", english="bird", category="animals", gender="m", language=LANGUAGE_KEY, id="oiseau"),
    VocabularyItem(french="poisson", english="fish", category="animals", gender="m", language=LANGUAGE_KEY, id="poisson"),
    VocabularyItem(french="cheval", english="horse", category="animals", gender="m", language=LANGUAGE_KEY, id="cheval"),
)


PRESENT_TENSE: Sequence[ConjugationPattern] = (
    ConjugationPattern("parler", "to speak", "parle", "parles", "parle", "parlons", "parlez", "parlent", LANGUAGE_KEY, id="parler"),
    ConjugationPattern("finir", "to finish", "finis", "finis", "finit", "finissons", "finissez", "finissent", LANGUAGE_KEY, id="finir"),
    ConjugationPattern("avoir", "to have", "ai", "as", "a", "avons", "avez", "ont", LANGUAGE_KEY, id="avoir"),
    ConjugationPattern("\u00eatre", "to be", "suis", "es", "est", "sommes", "\u00eates", "sont", LANGUAGE_KEY, id="etre"),
    ConjugationPattern("aller", "to go", "vais", "vas", "va", "allons", "allez", "vont", LANGUAGE_KEY, id="aller"),
)


SENTENCES: Sequence[Sentence] = (
    Sentence(
        "greeting_bonjour", "Bonjour.", "Hello.", ("greetings", "sentence_practice"), LANGUAGE_KEY,
        accepted_answers=("Hi.",), target_vocabulary_ids=("bonjour",),
        taught_construction="Bonjour is a complete greeting by itself.",
        target_notes=(SentenceTargetNote(
            "vocabulary", "bonjour", "bonjour", ("hello", "hi"),
            "bonjour means ‘hello’ or ‘good day’.",
            "Vocabulary lesson: use bonjour as a polite daytime greeting.",
        ),), metadata_validated=True,
    ),
    Sentence(
        "greeting_merci", "Merci.", "Thank you.", ("greetings", "sentence_practice"), LANGUAGE_KEY,
        accepted_answers=("Thanks.",), target_vocabulary_ids=("merci",),
        taught_construction="Merci is a complete expression of thanks.",
        target_notes=(SentenceTargetNote(
            "vocabulary", "merci", "merci", ("thank you", "thanks"),
            "merci means ‘thank you’.",
            "Vocabulary lesson: merci is the everyday way to say thank you.",
        ),), metadata_validated=True,
    ),
    Sentence(
        "food_pain", "Je mange du pain.", "I am eating bread.", ("food", "sentence_practice"), LANGUAGE_KEY,
        accepted_answers=("I eat bread.",), target_vocabulary_ids=("pain",),
        taught_construction="du introduces an unspecified amount of a masculine food.",
        target_notes=(SentenceTargetNote(
            "vocabulary", "pain", "pain", ("bread",),
            "pain means ‘bread’.",
            "Vocabulary lesson: pain is masculine; du pain means some bread.",
        ),), metadata_validated=True,
    ),
    Sentence(
        "home_chat_maison",
        "Le chat est dans la maison.",
        "The cat is in the house.",
        ("home", "animals", "sentence_practice"),
        LANGUAGE_KEY,
        accepted_answers=("The cat is inside the house.",),
        target_vocabulary_ids=("chat", "maison"),
        target_verb_form_ids=("etre:present:third_singular",),
        taught_construction="être dans + place expresses being in or inside a place.",
        target_notes=(
            SentenceTargetNote(
                "vocabulary", "chat", "chat", ("cat",), "chat means ‘cat’.",
                "Vocabulary lesson: un chat is a cat; the final t is silent.",
            ),
            SentenceTargetNote(
                "vocabulary", "maison", "maison", ("house", "home"), "maison means ‘house’ or ‘home’.",
                "Vocabulary lesson: la maison is the house or home.",
            ),
            SentenceTargetNote(
                "verb_form", "etre:present:third_singular", "est", ("is",),
                "est is the third-person singular present form of être.",
                "Verb lesson: il/elle est means he/she/it is; compare je suis and nous sommes.",
            ),
        ),
        metadata_validated=True,
    ),
)
