"""Exercise logic for the language practice toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import choice, random, shuffle
from typing import Callable, Dict, Iterable, List, Optional, Sequence

from .data import random_conjugation_pattern, random_vocabulary_item, sentences, vocabulary_items
from .language_registry import active_language_key
from .models import ConjugationPattern, Sentence, VocabularyItem
from .sentence_generator import generate_sentence


@dataclass
class ExerciseState:
    """State shared by exercises for tracking streaks and totals."""

    total_attempts: int = 0
    correct_attempts: int = 0
    current_streak: int = 0

    def register_attempt(self, correct: bool) -> None:
        self.total_attempts += 1
        if correct:
            self.correct_attempts += 1
            self.current_streak += 1
        else:
            self.current_streak = 0

    @property
    def accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.correct_attempts / self.total_attempts


@dataclass(frozen=True)
class Card:
    """Simple flashcard-style object with pronunciation helpers."""

    id: str
    french: str
    english: str
    ipa: str
    phonetic: str
    tags: Sequence[str] = ()

    @property
    def front_text(self) -> str:
        return self.french

    @property
    def back_lines(self) -> Sequence[str]:
        return (self.english, self.ipa, self.phonetic)


@dataclass
class FlashcardExercise:
    """Simple flashcard exercise that prompts for translations."""

    category: Optional[str] = None
    state: ExerciseState = field(default_factory=ExerciseState)
    current_item: VocabularyItem | None = None
    _history: List[VocabularyItem] = field(default_factory=list)
    _history_index: int = -1

    def next_prompt(self) -> VocabularyItem:
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.current_item = self._history[self._history_index]
            return self.current_item
        item = random_vocabulary_item(self.category)
        self._record_history(item)
        return item

    def previous_prompt(self) -> VocabularyItem | None:
        if self._history_index <= 0:
            return None
        self._history_index -= 1
        self.current_item = self._history[self._history_index]
        return self.current_item

    def has_previous(self) -> bool:
        return self._history_index > 0

    def set_category(self, category: Optional[str]) -> None:
        normalized = None if not category or category == "all" else category
        if normalized == self.category:
            return
        self.category = normalized
        self.reset_history()

    def reset_history(self) -> None:
        self._history.clear()
        self._history_index = -1
        self.current_item = None

    def _record_history(self, item: VocabularyItem) -> None:
        """Track cards so the user can move backwards."""

        if self._history_index < len(self._history) - 1:
            self._history = self._history[: self._history_index + 1]
        self._history.append(item)
        self._history_index = len(self._history) - 1
        self.current_item = item

    def check_answer(self, answer: str) -> bool:
        if self.current_item is None:
            self.next_prompt()
        assert self.current_item is not None  # for type checkers
        correct = answer.strip().lower() == self.current_item.english.lower()
        self.state.register_attempt(correct)
        return correct


@dataclass
class FlipCardExercise:
    """Provide flip-card memorization with French text on the front."""

    category: Optional[str] = None
    include_sentences: bool = True
    deck: List[Card] = field(default_factory=list)
    current_index: int = -1
    current_card: Card | None = None
    showing_front: bool = True
    state: ExerciseState = field(default_factory=ExerciseState)

    def __post_init__(self) -> None:
        if not self.deck:
            self.refresh_deck()

    def refresh_deck(self) -> None:
        category_filter = None if not self.category or self.category == "all" else self.category
        language = active_language_key()
        vocab_cards = [
            Card(
                id=f"{language}_vocab_{item.french}",
                french=item.french,
                english=item.english,
                ipa=item.ipa,
                phonetic=item.phonetic,
                tags=(item.category, "vocabulary"),
            )
            for item in vocabulary_items(category=category_filter)
        ]
        sentence_cards: List[Card] = []
        if self.include_sentences:
            for sentence in sentences():
                if category_filter and category_filter not in sentence.tags:
                    continue
                sentence_cards.append(
                    Card(
                        id=sentence.id,
                        french=sentence.french,
                        english=sentence.english,
                        ipa=sentence.ipa,
                        phonetic=sentence.phonetic,
                        tags=tuple(sentence.tags),
                    )
                )
        cards = vocab_cards + sentence_cards
        shuffle(cards)
        self.deck = cards
        self.current_index = -1
        self.current_card = None
        self.showing_front = True

    def next_card(self) -> Card | None:
        if not self.deck:
            self.refresh_deck()
        if not self.deck:
            self.current_card = None
            return None
        self.current_index = (self.current_index + 1) % len(self.deck)
        self.current_card = self.deck[self.current_index]
        self.showing_front = True
        return self.current_card

    def flip(self) -> Card | None:
        if not self.current_card:
            return None
        self.showing_front = not self.showing_front
        return self.current_card

    def mark_known(self, knew_card: bool) -> None:
        self.state.register_attempt(knew_card)

    def set_category(self, category: Optional[str]) -> None:
        self.category = category
        self.refresh_deck()


@dataclass
class ConjugationExercise:
    """Select a verb and pronoun to quiz present tense conjugations."""

    state: ExerciseState = field(default_factory=ExerciseState)
    current_pattern: ConjugationPattern | None = None
    current_index: int = 0

    def next_prompt(self) -> tuple[str, str]:
        pattern = random_conjugation_pattern()
        self.current_pattern = pattern
        self.current_index = pattern.pronouns.index("je")
        return pattern.infinitive, pattern.pronouns[self.current_index]

    def cycle_prompt(self) -> tuple[str, str]:
        if self.current_pattern is None:
            return self.next_prompt()
        self.current_index = (self.current_index + 1) % len(self.current_pattern.pronouns)
        return self.current_pattern.infinitive, self.current_pattern.pronouns[self.current_index]

    def previous_prompt(self) -> tuple[str, str]:
        if self.current_pattern is None:
            return self.next_prompt()
        self.current_index = (self.current_index - 1) % len(self.current_pattern.pronouns)
        return self.current_pattern.infinitive, self.current_pattern.pronouns[self.current_index]

    def check_answer(self, answer: str) -> bool:
        if self.current_pattern is None:
            self.next_prompt()
        assert self.current_pattern is not None
        expected = self.current_pattern.answers[self.current_index]
        correct = answer.strip().lower() == expected.lower()
        self.state.register_attempt(correct)
        return correct


@dataclass
class SentencePracticeExercise:
    """Provide a steady stream of sentences for reading practice."""

    category: Optional[str] = None
    use_generator: bool = True
    current_sentence: Sentence | None = None

    def __post_init__(self) -> None:
        self._static_pool = self._filter_sentences()

    def _filter_sentences(self) -> List[Sentence]:
        if not self.category or self.category == "all":
            return list(sentences())
        return [sentence for sentence in sentences() if self.category in sentence.tags]

    def set_category(self, category: Optional[str]) -> None:
        self.category = category
        self._static_pool = self._filter_sentences()

    def next_sentence(self) -> Sentence:
        use_static = self._static_pool and (not self.use_generator or random() < 0.4)
        if use_static:
            sentence = choice(self._static_pool)
        else:
            sentence = generate_sentence(self.category)
        self.current_sentence = sentence
        return sentence


class ExerciseRegistry:
    """Registry of exercises so the GUI can remain decoupled from logic."""

    def __init__(self) -> None:
        self._creators: Dict[str, Callable[[], object]] = {}

    def register(self, name: str, factory: Callable[[], object]) -> None:
        self._creators[name] = factory

    def create(self, name: str) -> object:
        if name not in self._creators:
            raise KeyError(f"Unknown exercise: {name}")
        return self._creators[name]()

    def names(self) -> Iterable[str]:
        return self._creators.keys()


def build_exercise_registry() -> ExerciseRegistry:
    registry = ExerciseRegistry()
    registry.register("Flashcards", FlashcardExercise)
    registry.register("Flip Cards", FlipCardExercise)
    registry.register("Sentence Practice", SentencePracticeExercise)
    registry.register("Conjugation", ConjugationExercise)
    return registry
