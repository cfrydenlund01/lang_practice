"""Static data sets for the Italian language module.

The pack intentionally mixes practical travel language, everyday conversation,
and core grammar vocabulary so that a beginner is not limited to labels for
objects at home.
"""

from __future__ import annotations

from typing import Sequence

from ...models import ConjugationPattern, Sentence, VocabularyItem

LANGUAGE_KEY = "italian"

ACCENTED_CHARACTERS: Sequence[str] = ("à", "è", "é", "ì", "ò", "ó", "ù")

VOCABULARY: Sequence[VocabularyItem] = (
    # Greetings and social language
    VocabularyItem("ciao", "hello", "greetings", part_of_speech="expression", tags=("informal", "greeting"), language=LANGUAGE_KEY),
    VocabularyItem("buongiorno", "good morning", "greetings", part_of_speech="expression", tags=("polite", "greeting"), language=LANGUAGE_KEY),
    VocabularyItem("buonasera", "good evening", "greetings", part_of_speech="expression", tags=("polite", "greeting"), language=LANGUAGE_KEY),
    VocabularyItem("arrivederci", "goodbye", "greetings", part_of_speech="expression", tags=("polite", "farewell"), language=LANGUAGE_KEY),
    VocabularyItem("a presto", "see you soon", "greetings", part_of_speech="expression", tags=("informal", "farewell"), language=LANGUAGE_KEY),
    VocabularyItem("per favore", "please", "greetings", part_of_speech="expression", tags=("polite",), language=LANGUAGE_KEY),
    VocabularyItem("grazie", "thank you", "greetings", part_of_speech="expression", tags=("polite",), language=LANGUAGE_KEY),
    VocabularyItem("prego", "you are welcome", "greetings", part_of_speech="expression", tags=("polite",), language=LANGUAGE_KEY),
    VocabularyItem("scusa", "sorry", "greetings", part_of_speech="expression", tags=("informal",), language=LANGUAGE_KEY),
    VocabularyItem("mi scusi", "excuse me", "greetings", part_of_speech="expression", tags=("formal", "polite"), language=LANGUAGE_KEY),
    VocabularyItem("piacere", "nice to meet you", "greetings", part_of_speech="expression", tags=("social",), language=LANGUAGE_KEY),

    # Food and ordering
    VocabularyItem("pane", "bread", "food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("formaggio", "cheese", "food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("acqua", "water", "food", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("mela", "apple", "food", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("vino", "wine", "food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("caffè", "coffee", "food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("tè", "tea", "food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("colazione", "breakfast", "food", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("pranzo", "lunch", "food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("cena", "dinner", "food", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("conto", "bill", "food", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("vegetariano", "vegetarian", "food", part_of_speech="adjective", tags=("dietary",), language=LANGUAGE_KEY),

    # Home and daily life
    VocabularyItem("casa", "house", "home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("appartamento", "apartment", "home", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("stanza", "room", "home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("sedia", "chair", "home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("porta", "door", "home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("finestra", "window", "home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("cucina", "kitchen", "home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("bagno", "bathroom", "home", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("chiave", "key", "home", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("libro", "book", "home", gender="m", language=LANGUAGE_KEY),

    # People, relationships, and animals
    VocabularyItem("persona", "person", "people", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("amico", "male friend", "people", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("amica", "female friend", "people", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("famiglia", "family", "people", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("bambino", "boy", "people", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("bambina", "girl", "people", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("insegnante", "teacher", "people", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("gatto", "cat", "animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("cane", "dog", "animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("uccello", "bird", "animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("pesce", "fish", "animals", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("cavallo", "horse", "animals", gender="m", language=LANGUAGE_KEY),

    # Travel, places, and directions
    VocabularyItem("stazione", "station", "travel", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("biglietto", "ticket", "travel", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("treno", "train", "travel", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("aeroporto", "airport", "travel", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("albergo", "hotel", "travel", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("prenotazione", "reservation", "travel", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("valigia", "suitcase", "travel", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("mappa", "map", "travel", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("strada", "street", "city", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("piazza", "square", "city", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("museo", "museum", "city", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("farmacia", "pharmacy", "city", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("ospedale", "hospital", "city", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("destra", "right", "directions", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("sinistra", "left", "directions", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("vicino", "near", "directions", part_of_speech="adjective", language=LANGUAGE_KEY),
    VocabularyItem("lontano", "far", "directions", part_of_speech="adjective", language=LANGUAGE_KEY),

    # Time, learning, work, and emotions
    VocabularyItem("oggi", "today", "time", part_of_speech="adverb", language=LANGUAGE_KEY),
    VocabularyItem("domani", "tomorrow", "time", part_of_speech="adverb", language=LANGUAGE_KEY),
    VocabularyItem("ieri", "yesterday", "time", part_of_speech="adverb", language=LANGUAGE_KEY),
    VocabularyItem("mattina", "morning", "time", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("sera", "evening", "time", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("ora", "hour", "time", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("scuola", "school", "learning", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("studente", "student", "learning", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("lingua", "language", "learning", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("lavoro", "work", "work", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("ufficio", "office", "work", gender="m", language=LANGUAGE_KEY),
    VocabularyItem("riunione", "meeting", "work", gender="f", language=LANGUAGE_KEY),
    VocabularyItem("felice", "happy", "feelings", part_of_speech="adjective", language=LANGUAGE_KEY),
    VocabularyItem("stanco", "tired", "feelings", part_of_speech="adjective", language=LANGUAGE_KEY),
    VocabularyItem("preoccupato", "worried", "feelings", part_of_speech="adjective", language=LANGUAGE_KEY),
    VocabularyItem("grande", "big", "descriptions", part_of_speech="adjective", language=LANGUAGE_KEY),
    VocabularyItem("piccolo", "small", "descriptions", part_of_speech="adjective", language=LANGUAGE_KEY),

    # Core verbs, included as translation cards as well as in conjugation practice.
    VocabularyItem("parlare", "to speak", "verbs", part_of_speech="verb", language=LANGUAGE_KEY),
    VocabularyItem("mangiare", "to eat", "verbs", part_of_speech="verb", language=LANGUAGE_KEY),
    VocabularyItem("bere", "to drink", "verbs", part_of_speech="verb", language=LANGUAGE_KEY),
    VocabularyItem("andare", "to go", "verbs", part_of_speech="verb", language=LANGUAGE_KEY),
    VocabularyItem("venire", "to come", "verbs", part_of_speech="verb", language=LANGUAGE_KEY),
    VocabularyItem("fare", "to make", "verbs", part_of_speech="verb", language=LANGUAGE_KEY),
    VocabularyItem("volere", "to want", "verbs", part_of_speech="verb", language=LANGUAGE_KEY),
    VocabularyItem("potere", "to be able to", "verbs", part_of_speech="verb", language=LANGUAGE_KEY),
)


PRESENT_TENSE: Sequence[ConjugationPattern] = (
    ConjugationPattern("parlare", "to speak", "parlo", "parli", "parla", "parliamo", "parlate", "parlano", LANGUAGE_KEY),
    ConjugationPattern("mangiare", "to eat", "mangio", "mangi", "mangia", "mangiamo", "mangiate", "mangiano", LANGUAGE_KEY),
    ConjugationPattern("dormire", "to sleep", "dormo", "dormi", "dorme", "dormiamo", "dormite", "dormono", LANGUAGE_KEY),
    ConjugationPattern("capire", "to understand", "capisco", "capisci", "capisce", "capiamo", "capite", "capiscono", LANGUAGE_KEY),
    ConjugationPattern("avere", "to have", "ho", "hai", "ha", "abbiamo", "avete", "hanno", LANGUAGE_KEY),
    ConjugationPattern("essere", "to be", "sono", "sei", "è", "siamo", "siete", "sono", LANGUAGE_KEY),
    ConjugationPattern("andare", "to go", "vado", "vai", "va", "andiamo", "andate", "vanno", LANGUAGE_KEY),
    ConjugationPattern("fare", "to do / make", "faccio", "fai", "fa", "facciamo", "fate", "fanno", LANGUAGE_KEY),
    ConjugationPattern("venire", "to come", "vengo", "vieni", "viene", "veniamo", "venite", "vengono", LANGUAGE_KEY),
    ConjugationPattern("prendere", "to take", "prendo", "prendi", "prende", "prendiamo", "prendete", "prendono", LANGUAGE_KEY),
    ConjugationPattern("bere", "to drink", "bevo", "bevi", "beve", "beviamo", "bevete", "bevono", LANGUAGE_KEY),
    ConjugationPattern("uscire", "to go out / leave", "esco", "esci", "esce", "usciamo", "uscite", "escono", LANGUAGE_KEY),
    ConjugationPattern("sapere", "to know", "so", "sai", "sa", "sappiamo", "sapete", "sanno", LANGUAGE_KEY),
    ConjugationPattern("potere", "to be able to / can", "posso", "puoi", "può", "possiamo", "potete", "possono", LANGUAGE_KEY),
    ConjugationPattern("volere", "to want", "voglio", "vuoi", "vuole", "vogliamo", "volete", "vogliono", LANGUAGE_KEY),
    ConjugationPattern("dovere", "to have to / must", "devo", "devi", "deve", "dobbiamo", "dovete", "devono", LANGUAGE_KEY),
    ConjugationPattern("studiare", "to study", "studio", "studi", "studia", "studiamo", "studiate", "studiano", LANGUAGE_KEY),
)


SENTENCES: Sequence[Sentence] = (
    Sentence("greeting_ciao", "Ciao.", "Hello.", ("greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("greeting_buongiorno", "Buongiorno, come va?", "Good morning, how are you?", ("greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("greeting_piace", "Piacere di conoscerti.", "Nice to meet you.", ("greetings", "people", "sentence_practice"), LANGUAGE_KEY),
    Sentence("greeting_scusi", "Mi scusi, può aiutarmi?", "Excuse me, can you help me?", ("greetings", "travel", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_pane", "Mangio il pane.", "I am eating bread.", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_order", "Vorrei un caffè, per favore.", "I would like a coffee, please.", ("food", "greetings", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_bill", "Il conto, per favore.", "The bill, please.", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_water", "Posso avere dell'acqua?", "Can I have some water?", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence("food_vegetarian", "Sono vegetariano.", "I am vegetarian.", ("food", "sentence_practice"), LANGUAGE_KEY),
    Sentence("home_gatto_casa", "Il gatto è in casa.", "The cat is in the house.", ("home", "animals", "sentence_practice"), LANGUAGE_KEY),
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
