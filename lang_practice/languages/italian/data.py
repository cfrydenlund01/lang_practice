"""Static data sets for the Italian language module.

The pack intentionally mixes practical travel language, everyday conversation,
and core grammar vocabulary so that a beginner is not limited to labels for
objects at home.
"""

from __future__ import annotations

from typing import Sequence

from ...models import ConjugationPattern, Sentence, SentenceTargetNote, VocabularyItem

LANGUAGE_KEY = "italian"

ACCENTED_CHARACTERS: Sequence[str] = ("à", "è", "é", "ì", "ò", "ó", "ù")

VOCABULARY: Sequence[VocabularyItem] = (
    # Greetings and social language
    VocabularyItem("ciao", "hello", "greetings", part_of_speech="expression", tags=("informal", "greeting"), language=LANGUAGE_KEY, id="ciao"),
    VocabularyItem("buongiorno", "good morning", "greetings", part_of_speech="expression", tags=("polite", "greeting"), language=LANGUAGE_KEY, id="buongiorno"),
    VocabularyItem("buonasera", "good evening", "greetings", part_of_speech="expression", tags=("polite", "greeting"), language=LANGUAGE_KEY, id="buonasera"),
    VocabularyItem("arrivederci", "goodbye", "greetings", part_of_speech="expression", tags=("polite", "farewell"), language=LANGUAGE_KEY, id="arrivederci"),
    VocabularyItem("a presto", "see you soon", "greetings", part_of_speech="expression", tags=("informal", "farewell"), language=LANGUAGE_KEY, id="a_presto"),
    VocabularyItem("per favore", "please", "greetings", part_of_speech="expression", tags=("polite",), language=LANGUAGE_KEY, id="per_favore"),
    VocabularyItem("grazie", "thank you", "greetings", part_of_speech="expression", tags=("polite",), language=LANGUAGE_KEY, id="grazie"),
    VocabularyItem("prego", "you are welcome", "greetings", part_of_speech="expression", tags=("polite",), language=LANGUAGE_KEY, id="prego"),
    VocabularyItem("scusa", "sorry", "greetings", part_of_speech="expression", tags=("informal",), language=LANGUAGE_KEY, id="scusa"),
    VocabularyItem("mi scusi", "excuse me", "greetings", part_of_speech="expression", tags=("formal", "polite"), language=LANGUAGE_KEY, id="mi_scusi"),
    VocabularyItem("piacere", "nice to meet you", "greetings", part_of_speech="expression", tags=("social",), language=LANGUAGE_KEY, id="piacere"),

    # Food and ordering
    VocabularyItem("pane", "bread", "food", gender="m", language=LANGUAGE_KEY, id="pane"),
    VocabularyItem("formaggio", "cheese", "food", gender="m", language=LANGUAGE_KEY, id="formaggio"),
    VocabularyItem("acqua", "water", "food", gender="f", language=LANGUAGE_KEY, id="acqua"),
    VocabularyItem("mela", "apple", "food", gender="f", language=LANGUAGE_KEY, id="mela"),
    VocabularyItem("vino", "wine", "food", gender="m", language=LANGUAGE_KEY, id="vino"),
    VocabularyItem("caffè", "coffee", "food", gender="m", language=LANGUAGE_KEY, id="caffe"),
    VocabularyItem("tè", "tea", "food", gender="m", language=LANGUAGE_KEY, id="te"),
    VocabularyItem("colazione", "breakfast", "food", gender="f", language=LANGUAGE_KEY, id="colazione"),
    VocabularyItem("pranzo", "lunch", "food", gender="m", language=LANGUAGE_KEY, id="pranzo"),
    VocabularyItem("cena", "dinner", "food", gender="f", language=LANGUAGE_KEY, id="cena"),
    VocabularyItem("conto", "bill", "food", gender="m", language=LANGUAGE_KEY, id="conto"),
    VocabularyItem("vegetariano", "vegetarian", "food", part_of_speech="adjective", tags=("dietary",), language=LANGUAGE_KEY, id="vegetariano"),

    # Home and daily life
    VocabularyItem("casa", "house", "home", gender="f", language=LANGUAGE_KEY, id="casa"),
    VocabularyItem("appartamento", "apartment", "home", gender="m", language=LANGUAGE_KEY, id="appartamento"),
    VocabularyItem("stanza", "room", "home", gender="f", language=LANGUAGE_KEY, id="stanza"),
    VocabularyItem("sedia", "chair", "home", gender="f", language=LANGUAGE_KEY, id="sedia"),
    VocabularyItem("porta", "door", "home", gender="f", language=LANGUAGE_KEY, id="porta"),
    VocabularyItem("finestra", "window", "home", gender="f", language=LANGUAGE_KEY, id="finestra"),
    VocabularyItem("cucina", "kitchen", "home", gender="f", language=LANGUAGE_KEY, id="cucina"),
    VocabularyItem("bagno", "bathroom", "home", gender="m", language=LANGUAGE_KEY, id="bagno"),
    VocabularyItem("chiave", "key", "home", gender="f", language=LANGUAGE_KEY, id="chiave"),
    VocabularyItem("libro", "book", "home", gender="m", language=LANGUAGE_KEY, id="libro"),

    # People, relationships, and animals
    VocabularyItem("persona", "person", "people", gender="f", language=LANGUAGE_KEY, id="persona"),
    VocabularyItem("amico", "male friend", "people", gender="m", language=LANGUAGE_KEY, id="amico"),
    VocabularyItem("amica", "female friend", "people", gender="f", language=LANGUAGE_KEY, id="amica"),
    VocabularyItem("famiglia", "family", "people", gender="f", language=LANGUAGE_KEY, id="famiglia"),
    VocabularyItem("bambino", "boy", "people", gender="m", language=LANGUAGE_KEY, id="bambino"),
    VocabularyItem("bambina", "girl", "people", gender="f", language=LANGUAGE_KEY, id="bambina"),
    VocabularyItem("insegnante", "teacher", "people", gender="m", language=LANGUAGE_KEY, id="insegnante"),
    VocabularyItem("gatto", "cat", "animals", gender="m", language=LANGUAGE_KEY, id="gatto"),
    VocabularyItem("cane", "dog", "animals", gender="m", language=LANGUAGE_KEY, id="cane"),
    VocabularyItem("uccello", "bird", "animals", gender="m", language=LANGUAGE_KEY, id="uccello"),
    VocabularyItem("pesce", "fish", "animals", gender="m", language=LANGUAGE_KEY, id="pesce"),
    VocabularyItem("cavallo", "horse", "animals", gender="m", language=LANGUAGE_KEY, id="cavallo"),

    # Travel, places, and directions
    VocabularyItem("stazione", "station", "travel", gender="f", language=LANGUAGE_KEY, id="stazione"),
    VocabularyItem("biglietto", "ticket", "travel", gender="m", language=LANGUAGE_KEY, id="biglietto"),
    VocabularyItem("treno", "train", "travel", gender="m", language=LANGUAGE_KEY, id="treno"),
    VocabularyItem("aeroporto", "airport", "travel", gender="m", language=LANGUAGE_KEY, id="aeroporto"),
    VocabularyItem("albergo", "hotel", "travel", gender="m", language=LANGUAGE_KEY, id="albergo"),
    VocabularyItem("prenotazione", "reservation", "travel", gender="f", language=LANGUAGE_KEY, id="prenotazione"),
    VocabularyItem("valigia", "suitcase", "travel", gender="f", language=LANGUAGE_KEY, id="valigia"),
    VocabularyItem("mappa", "map", "travel", gender="f", language=LANGUAGE_KEY, id="mappa"),
    VocabularyItem("strada", "street", "city", gender="f", language=LANGUAGE_KEY, id="strada"),
    VocabularyItem("piazza", "square", "city", gender="f", language=LANGUAGE_KEY, id="piazza"),
    VocabularyItem("museo", "museum", "city", gender="m", language=LANGUAGE_KEY, id="museo"),
    VocabularyItem("farmacia", "pharmacy", "city", gender="f", language=LANGUAGE_KEY, id="farmacia"),
    VocabularyItem("ospedale", "hospital", "city", gender="m", language=LANGUAGE_KEY, id="ospedale"),
    VocabularyItem("destra", "right", "directions", gender="f", language=LANGUAGE_KEY, id="destra"),
    VocabularyItem("sinistra", "left", "directions", gender="f", language=LANGUAGE_KEY, id="sinistra"),
    VocabularyItem("vicino", "near", "directions", part_of_speech="adjective", language=LANGUAGE_KEY, id="vicino"),
    VocabularyItem("lontano", "far", "directions", part_of_speech="adjective", language=LANGUAGE_KEY, id="lontano"),

    # Time, learning, work, and emotions
    VocabularyItem("oggi", "today", "time", part_of_speech="adverb", language=LANGUAGE_KEY, id="oggi"),
    VocabularyItem("domani", "tomorrow", "time", part_of_speech="adverb", language=LANGUAGE_KEY, id="domani"),
    VocabularyItem("ieri", "yesterday", "time", part_of_speech="adverb", language=LANGUAGE_KEY, id="ieri"),
    VocabularyItem("mattina", "morning", "time", gender="f", language=LANGUAGE_KEY, id="mattina"),
    VocabularyItem("sera", "evening", "time", gender="f", language=LANGUAGE_KEY, id="sera"),
    VocabularyItem("ora", "hour", "time", gender="f", language=LANGUAGE_KEY, id="ora"),
    VocabularyItem("scuola", "school", "learning", gender="f", language=LANGUAGE_KEY, id="scuola"),
    VocabularyItem("studente", "student", "learning", gender="m", language=LANGUAGE_KEY, id="studente"),
    VocabularyItem("lingua", "language", "learning", gender="f", language=LANGUAGE_KEY, id="lingua"),
    VocabularyItem("lavoro", "work", "work", gender="m", language=LANGUAGE_KEY, id="lavoro"),
    VocabularyItem("ufficio", "office", "work", gender="m", language=LANGUAGE_KEY, id="ufficio"),
    VocabularyItem("riunione", "meeting", "work", gender="f", language=LANGUAGE_KEY, id="riunione"),
    VocabularyItem("felice", "happy", "feelings", part_of_speech="adjective", language=LANGUAGE_KEY, id="felice"),
    VocabularyItem("stanco", "tired", "feelings", part_of_speech="adjective", language=LANGUAGE_KEY, id="stanco"),
    VocabularyItem("preoccupato", "worried", "feelings", part_of_speech="adjective", language=LANGUAGE_KEY, id="preoccupato"),
    VocabularyItem("grande", "big", "descriptions", part_of_speech="adjective", language=LANGUAGE_KEY, id="grande"),
    VocabularyItem("piccolo", "small", "descriptions", part_of_speech="adjective", language=LANGUAGE_KEY, id="piccolo"),

    # Core verbs, included as translation cards as well as in conjugation practice.
    VocabularyItem("parlare", "to speak", "verbs", part_of_speech="verb", language=LANGUAGE_KEY, id="parlare"),
    VocabularyItem("mangiare", "to eat", "verbs", part_of_speech="verb", language=LANGUAGE_KEY, id="mangiare"),
    VocabularyItem("bere", "to drink", "verbs", part_of_speech="verb", language=LANGUAGE_KEY, id="bere"),
    VocabularyItem("andare", "to go", "verbs", part_of_speech="verb", language=LANGUAGE_KEY, id="andare"),
    VocabularyItem("venire", "to come", "verbs", part_of_speech="verb", language=LANGUAGE_KEY, id="venire"),
    VocabularyItem("fare", "to make", "verbs", part_of_speech="verb", language=LANGUAGE_KEY, id="fare"),
    VocabularyItem("volere", "to want", "verbs", part_of_speech="verb", language=LANGUAGE_KEY, id="volere"),
    VocabularyItem("potere", "to be able to", "verbs", part_of_speech="verb", language=LANGUAGE_KEY, id="potere"),
)


PRESENT_TENSE: Sequence[ConjugationPattern] = (
    ConjugationPattern("parlare", "to speak", "parlo", "parli", "parla", "parliamo", "parlate", "parlano", LANGUAGE_KEY, id="parlare"),
    ConjugationPattern("mangiare", "to eat", "mangio", "mangi", "mangia", "mangiamo", "mangiate", "mangiano", LANGUAGE_KEY, id="mangiare"),
    ConjugationPattern("dormire", "to sleep", "dormo", "dormi", "dorme", "dormiamo", "dormite", "dormono", LANGUAGE_KEY, id="dormire"),
    ConjugationPattern("capire", "to understand", "capisco", "capisci", "capisce", "capiamo", "capite", "capiscono", LANGUAGE_KEY, id="capire"),
    ConjugationPattern("avere", "to have", "ho", "hai", "ha", "abbiamo", "avete", "hanno", LANGUAGE_KEY, id="avere"),
    ConjugationPattern("essere", "to be", "sono", "sei", "è", "siamo", "siete", "sono", LANGUAGE_KEY, id="essere"),
    ConjugationPattern("andare", "to go", "vado", "vai", "va", "andiamo", "andate", "vanno", LANGUAGE_KEY, id="andare"),
    ConjugationPattern("fare", "to do / make", "faccio", "fai", "fa", "facciamo", "fate", "fanno", LANGUAGE_KEY, id="fare"),
    ConjugationPattern("venire", "to come", "vengo", "vieni", "viene", "veniamo", "venite", "vengono", LANGUAGE_KEY, id="venire"),
    ConjugationPattern("prendere", "to take", "prendo", "prendi", "prende", "prendiamo", "prendete", "prendono", LANGUAGE_KEY, id="prendere"),
    ConjugationPattern("bere", "to drink", "bevo", "bevi", "beve", "beviamo", "bevete", "bevono", LANGUAGE_KEY, id="bere"),
    ConjugationPattern("uscire", "to go out / leave", "esco", "esci", "esce", "usciamo", "uscite", "escono", LANGUAGE_KEY, id="uscire"),
    ConjugationPattern("sapere", "to know", "so", "sai", "sa", "sappiamo", "sapete", "sanno", LANGUAGE_KEY, id="sapere"),
    ConjugationPattern("potere", "to be able to / can", "posso", "puoi", "può", "possiamo", "potete", "possono", LANGUAGE_KEY, id="potere"),
    ConjugationPattern("volere", "to want", "voglio", "vuoi", "vuole", "vogliamo", "volete", "vogliono", LANGUAGE_KEY, id="volere"),
    ConjugationPattern("dovere", "to have to / must", "devo", "devi", "deve", "dobbiamo", "dovete", "devono", LANGUAGE_KEY, id="dovere"),
    ConjugationPattern("studiare", "to study", "studio", "studi", "studia", "studiamo", "studiate", "studiano", LANGUAGE_KEY, id="studiare"),
)


SENTENCES: Sequence[Sentence] = (
    Sentence(
        "greeting_ciao", "Ciao.", "Hello.", ("greetings", "sentence_practice"), LANGUAGE_KEY,
        accepted_answers=("Hi.",), target_vocabulary_ids=("ciao",),
        taught_construction="Ciao is a complete informal greeting.",
        target_notes=(SentenceTargetNote(
            "vocabulary", "ciao", "ciao", ("hello", "hi"), "ciao means ‘hello’ or ‘hi’.",
            "Vocabulary lesson: ciao is informal and can mean hello or goodbye.",
        ),), metadata_validated=True,
    ),
    Sentence(
        "greeting_buongiorno", "Buongiorno, come va?", "Good morning, how are you?", ("greetings", "sentence_practice"), LANGUAGE_KEY,
        accepted_answers=("Good morning, how is it going?",), target_vocabulary_ids=("buongiorno",),
        taught_construction="come va? literally asks how it is going.",
        target_notes=(SentenceTargetNote(
            "vocabulary", "buongiorno", "buongiorno", ("good morning",),
            "buongiorno means ‘good morning’ or ‘good day’.",
            "Vocabulary lesson: use buongiorno as a polite daytime greeting.",
        ),), metadata_validated=True,
    ),
    Sentence("greeting_piace", "Piacere di conoscerti.", "Nice to meet you.", ("greetings", "people", "sentence_practice"), LANGUAGE_KEY),
    Sentence("greeting_scusi", "Mi scusi, può aiutarmi?", "Excuse me, can you help me?", ("greetings", "travel", "sentence_practice"), LANGUAGE_KEY),
    Sentence(
        "food_pane", "Mangio il pane.", "I am eating bread.", ("food", "sentence_practice"), LANGUAGE_KEY,
        accepted_answers=("I eat bread.",), target_vocabulary_ids=("pane",),
        target_verb_form_ids=("mangiare:present:first_singular",),
        taught_construction="Italian often omits io because the -o verb ending already identifies the subject.",
        target_notes=(
            SentenceTargetNote(
                "vocabulary", "pane", "pane", ("bread",), "pane means ‘bread’.",
                "Vocabulary lesson: il pane means the bread.",
            ),
            SentenceTargetNote(
                "verb_form", "mangiare:present:first_singular", "mangio", ("eat", "eating"),
                "mangio is the io present form of mangiare.",
                "Verb lesson: remove -are and add -o for io: mangiare → mangio.",
            ),
        ), metadata_validated=True,
    ),
    Sentence("food_order", "Vorrei un caffè, per favore.", "I would like a coffee, please.", ("food", "greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_bill", "Il conto, per favore.", "The bill, please.", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_water", "Posso avere dell'acqua?", "Can I have some water?", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_vegetarian", "Sono vegetariano.", "I am vegetarian.", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence(
        "home_gatto_casa", "Il gatto è in casa.", "The cat is in the house.", ("home", "animals", "sentence_practice"), LANGUAGE_KEY,
        accepted_answers=("The cat is at home.",), target_vocabulary_ids=("gatto", "casa"),
        target_verb_form_ids=("essere:present:third_singular",),
        taught_construction="essere in + place expresses being in or at a place.",
        target_notes=(
            SentenceTargetNote(
                "vocabulary", "gatto", "gatto", ("cat",), "gatto means ‘cat’.",
                "Vocabulary lesson: il gatto is the cat.",
            ),
            SentenceTargetNote(
                "vocabulary", "casa", "casa", ("house", "home"), "casa means ‘house’ or ‘home’.",
                "Vocabulary lesson: in casa commonly means at home.",
            ),
            SentenceTargetNote(
                "verb_form", "essere:present:third_singular", "è", ("is",),
                "è is the third-person singular present form of essere.",
                "Verb lesson: lui/lei è means he/she/it is; the accent distinguishes è from e (‘and’).",
            ),
        ), metadata_validated=True,
    ),
    Sentence("home_cucina", "La cucina è grande.", "The kitchen is big.", ("home", "sentence_practice"), LANGUAGE_KEY),
    Sentence("description_small", "L'appartamento è piccolo.", "The apartment is small.", ("home", "descriptions", "sentence_practice"), LANGUAGE_KEY),
    Sentence("home_key", "Dov'è la chiave?", "Where is the key?", ("home", "sentence_practice"), LANGUAGE_KEY),
    Sentence("people_friend", "La mia amica parla italiano.", "My friend speaks Italian.", ("people", "learning", "sentence_practice"), LANGUAGE_KEY),
    Sentence("people_family", "La mia famiglia è grande.", "My family is big.", ("people", "sentence_practice"), LANGUAGE_KEY),
    Sentence("travel_station", "Dov'è la stazione?", "Where is the station?", ("travel", "directions", "sentence_practice"), LANGUAGE_KEY),
    Sentence("travel_ticket", "Vorrei un biglietto per Roma.", "I would like a ticket to Rome.", ("travel", "sentence_practice"), LANGUAGE_KEY),
    Sentence("travel_train", "Il treno parte alle otto.", "The train leaves at eight.", ("travel", "time", "sentence_practice"), LANGUAGE_KEY),
    Sentence("travel_reservation", "Ho una prenotazione.", "I have a reservation.", ("travel", "sentence_practice"), LANGUAGE_KEY),
    Sentence("travel_hotel", "L'albergo è vicino alla stazione.", "The hotel is near the station.", ("travel", "directions", "sentence_practice"), LANGUAGE_KEY),
    Sentence("city_pharmacy", "C'è una farmacia qui vicino?", "Is there a pharmacy nearby?", ("city", "health", "sentence_practice"), LANGUAGE_KEY),
    Sentence("directions_right", "Giri a destra dopo la piazza.", "Turn right after the square.", ("directions", "city", "sentence_practice"), LANGUAGE_KEY),
    Sentence("directions_left", "Il museo è a sinistra.", "The museum is on the left.", ("directions", "city", "sentence_practice"), LANGUAGE_KEY),
    Sentence("learning_slowly", "Può parlare più lentamente?", "Can you speak more slowly?", ("learning", "greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("learning_understand", "Non capisco, può ripetere?", "I do not understand; can you repeat?", ("learning", "greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("learning_study", "Studio italiano ogni giorno.", "I study Italian every day.", ("learning", "time", "sentence_practice"), LANGUAGE_KEY),
    Sentence("verbs_want", "Voglio bere un tè.", "I want to drink a tea.", ("verbs", "food", "sentence_practice"), LANGUAGE_KEY),
    Sentence("work_meeting", "La riunione è alle nove.", "The meeting is at nine.", ("work", "time", "sentence_practice"), LANGUAGE_KEY),
    Sentence("work_office", "L'ufficio è chiuso oggi.", "The office is closed today.", ("work", "time", "sentence_practice"), LANGUAGE_KEY),
    Sentence("feelings_happy", "Sono felice oggi.", "I am happy today.", ("feelings", "time", "sentence_practice"), LANGUAGE_KEY),
    Sentence("feelings_tired", "Sono molto stanco.", "I am very tired.", ("feelings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("health_allergy", "Ho un'allergia alle noci.", "I have a nut allergy.", ("health", "sentence_practice"), LANGUAGE_KEY),
    Sentence("emergency_help", "Ho bisogno di aiuto.", "I need help.", ("health", "travel", "sentence_practice"), LANGUAGE_KEY),
    Sentence("time_today", "Oggi lavoro da casa.", "Today I work from home.", ("time", "work", "home", "sentence_practice"), LANGUAGE_KEY),
    Sentence("time_tomorrow", "Domani andiamo al museo.", "Tomorrow we are going to the museum.", ("time", "city", "sentence_practice"), LANGUAGE_KEY),
)
