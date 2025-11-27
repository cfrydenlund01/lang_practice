"""Tkinter based GUI for modular language practice activities."""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from .audio import play_audio
from .data import accented_characters, categories, vocabulary_items
from .exercises import (
    ConjugationExercise,
    ExerciseRegistry,
    FlashcardExercise,
    FlipCardExercise,
    SentencePracticeExercise,
    build_exercise_registry,
)
from .language_registry import active_language_key, available_modules, get_active_module, set_active_module
from .models import VocabularyItem
from .pronunciation import explain_pronunciation, to_ipa, to_phonetic
from .tts_client import available as tts_client_available, synthesize_to_file

_tts_flag = os.getenv("LANG_PRACTICE_TTS_ENABLED", os.getenv("FRENCH_TTS_ENABLED", "1"))
ENABLE_TTS = (_tts_flag or "1").lower() not in {"0", "false", "off"}


def category_values() -> list[str]:
    return ["all", *categories(vocabulary_items())]


def language_label() -> str:
    return get_active_module().label


def tts_available() -> bool:
    return ENABLE_TTS and tts_client_available()


def play_tts_async(
    text: str,
    *,
    lang: str | None = None,
    on_start: Callable[[], None] | None = None,
    on_complete: Callable[[bool], None] | None = None,
) -> None:
    if not text or not tts_available():
        if on_complete:
            on_complete(False)
        return

    def _worker() -> None:
        success = False
        if on_start:
            on_start()
        try:
            language_code = lang or get_active_module().tts_lang
            path = synthesize_to_file(text, lang=language_code)
            if path:
                success = play_audio(path)
        finally:
            if on_complete:
                on_complete(success)

    threading.Thread(target=_worker, daemon=True).start()


class AccentToolbar(ttk.Frame):
    """Toolbar that inserts accented characters into a linked entry widget."""

    def __init__(self, master: tk.Misc, target: tk.Entry, *, characters: tuple[str, ...] | None = None) -> None:
        super().__init__(master, padding=(4, 2))
        self.target = target
        self.characters = characters or tuple(accented_characters())
        self._build_buttons()

    def _build_buttons(self) -> None:
        for char in self.characters:
            button = ttk.Button(self, text=char, width=3)
            button.configure(command=lambda value=char: self._insert(value))
            button.pack(side=tk.LEFT, padx=1)

    def _insert(self, value: str) -> None:
        self.target.insert(tk.INSERT, value)
        self.target.focus_set()


class StatsBar(ttk.Frame):
    """Simple bar displaying exercise statistics."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=(4, 2))
        self.accuracy_var = tk.StringVar(value="Accuracy: 0%")
        self.streak_var = tk.StringVar(value="Streak: 0")
        ttk.Label(self, textvariable=self.accuracy_var).pack(side=tk.LEFT, padx=4)
        ttk.Label(self, textvariable=self.streak_var).pack(side=tk.LEFT, padx=4)

    def update_state(self, accuracy: float, streak: int) -> None:
        self.accuracy_var.set(f"Accuracy: {accuracy:.0%}")
        self.streak_var.set(f"Streak: {streak}")


class TTSStatusIndicator(ttk.Frame):
    """Compact status indicator that shows TTS download progress."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=(0, 0))
        self.message_var = tk.StringVar(value="")
        self._hide_job: str | None = None
        self._running = False

        ttk.Label(self, textvariable=self.message_var, font=("Helvetica", 9), foreground="gray40").grid(
            row=0, column=0, sticky="w"
        )
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=110)
        self.progress.grid(row=1, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)

    def start(self) -> None:
        self._set_message("Requesting audio…")
        if not self._running:
            self.progress.start(12)
            self._running = True

    def finish(self, success: bool) -> None:
        if self._running:
            self.progress.stop()
            self._running = False
        self._set_message("Audio ready" if success else "Audio unavailable")
        self._hide_job = self.after(1500, self._clear_message)

    def _clear_message(self) -> None:
        self._hide_job = None
        self.message_var.set("")

    def _set_message(self, message: str) -> None:
        if self._hide_job:
            self.after_cancel(self._hide_job)
            self._hide_job = None
        self.message_var.set(message)


class PronunciationHelpPanel(ttk.Frame):
    """Side panel showing plain-language pronunciation tips from the guide."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=(8, 8))
        ttk.Label(self, text="Pronunciation guide", font=("Helvetica", 11, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        self.text = tk.Text(
            self,
            width=40,
            wrap=tk.WORD,
            font=("Helvetica", 10),
        )
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set, state="disabled")
        self.text.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.set_text("Select a word or sentence to see pronunciation tips based on the guide.")

    def set_text(self, content: str) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")


def _queue_tts_request(widget: tk.Misc, indicator: TTSStatusIndicator, text: str, *, lang: str | None = None) -> None:
    """Trigger a TTS request while updating an indicator from the Tk thread."""

    if not text:
        return

    def _start() -> None:
        widget.after(0, indicator.start)

    def _finish(success: bool) -> None:
        widget.after(0, indicator.finish, success)

    play_tts_async(text, lang=lang, on_start=_start, on_complete=_finish)


class FlashcardTab(ttk.Frame):
    """Tab widget that wires the flashcard exercise into the UI."""

    def __init__(
        self,
        master: tk.Misc,
        exercise: FlashcardExercise,
        help_panel: PronunciationHelpPanel | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self._help_panel = help_panel
        self.prompt_var = tk.StringVar(value="Press Next to start")
        self.ipa_var = tk.StringVar()
        self.phonetic_var = tk.StringVar()
        self.feedback_var = tk.StringVar()
        self.answer_var = tk.StringVar()
        self.category_var = tk.StringVar(value="all")

        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="Category:").grid(row=0, column=0, sticky="w")
        cat_values = category_values()
        ttk.OptionMenu(self, self.category_var, self.category_var.get(), *cat_values, command=self._change_category).grid(
            row=0, column=1, sticky="w"
        )

        ttk.Label(self, textvariable=self.prompt_var, font=("Helvetica", 16, "bold")).grid(
            row=1, column=0, columnspan=2, pady=(12, 4), sticky="w"
        )
        listen_state = tk.NORMAL if tts_available() else tk.DISABLED
        listen_frame = ttk.Frame(self)
        listen_frame.grid(row=1, column=2, sticky="ne")
        ttk.Button(listen_frame, text="Listen", command=self._play_audio, state=listen_state).grid(
            row=0, column=0, sticky="ew"
        )
        listen_frame.columnconfigure(0, weight=1)
        self.listen_indicator = TTSStatusIndicator(listen_frame)
        self.listen_indicator.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Label(self, textvariable=self.ipa_var, font=("Helvetica", 12, "italic"), foreground="gray25").grid(
            row=2, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(self, textvariable=self.phonetic_var, font=("Helvetica", 12), foreground="gray35").grid(
            row=3, column=0, columnspan=3, sticky="w"
        )

        answer_entry = ttk.Entry(self, textvariable=self.answer_var, width=30)
        answer_entry.grid(row=4, column=0, columnspan=2, pady=4, sticky="we")
        AccentToolbar(self, answer_entry).grid(row=5, column=0, columnspan=2, sticky="w")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=2, rowspan=2, padx=(8, 0), sticky="ns")
        ttk.Button(button_frame, text="Check", command=self._check_answer).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Reveal", command=self._reveal_answer).pack(fill=tk.X, pady=2)
        self.prev_button = ttk.Button(button_frame, text="Previous", command=self._previous, state=tk.DISABLED)
        self.prev_button.pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Next", command=self._next).pack(fill=tk.X, pady=2)

        ttk.Label(self, textvariable=self.feedback_var, foreground="steelblue").grid(
            row=6, column=0, columnspan=3, pady=(8, 0), sticky="w"
        )

        self.stats = StatsBar(self)
        self.stats.grid(row=7, column=0, columnspan=3, sticky="we", pady=(12, 0))

        for i in range(3):
            self.columnconfigure(i, weight=1)

    def _change_category(self, category: str) -> None:
        self.exercise.set_category(category)
        self._next()

    def _next(self) -> None:
        item = self.exercise.next_prompt()
        self._display_item(item)

    def _previous(self) -> None:
        item = self.exercise.previous_prompt()
        if item is None:
            self.feedback_var.set("No previous card available.")
            self._update_previous_state()
            return
        self._display_item(item)

    def _display_item(self, item: VocabularyItem) -> None:
        self.prompt_var.set(f"Translate: {item.french}")
        self._update_pronunciation(item)
        self.answer_var.set("")
        self.feedback_var.set("")
        self._update_previous_state()
        self._update_help(item.french)

    def _update_previous_state(self) -> None:
        state = tk.NORMAL if self.exercise.has_previous() else tk.DISABLED
        self.prev_button.configure(state=state)

    def _check_answer(self) -> None:
        if not self.answer_var.get():
            self.feedback_var.set("Type your answer first.")
            return
        correct = self.exercise.check_answer(self.answer_var.get())
        if correct:
            self.feedback_var.set("Correct! 🎉")
            self._next()
        else:
            assert self.exercise.current_item is not None
            self.feedback_var.set(f"Not quite. Answer: {self.exercise.current_item.english}")
        self._refresh_stats()

    def _reveal_answer(self) -> None:
        if self.exercise.current_item:
            self.feedback_var.set(f"Answer: {self.exercise.current_item.english}")
            self._update_pronunciation(self.exercise.current_item)

    def _refresh_stats(self) -> None:
        state = self.exercise.state
        self.stats.update_state(state.accuracy, state.current_streak)

    def _update_pronunciation(self, item: VocabularyItem | None) -> None:
        if item is None:
            self.ipa_var.set("")
            self.phonetic_var.set("")
            return
        self.ipa_var.set(item.ipa)
        self.phonetic_var.set(item.phonetic)

    def _play_audio(self) -> None:
        if self.exercise.current_item:
            _queue_tts_request(self, self.listen_indicator, self.exercise.current_item.french)

    def _update_help(self, text: str | None) -> None:
        if self._help_panel is None or not text:
            return
        explanation = explain_pronunciation(text)
        self._help_panel.set_text(explanation)



class ConjugationTab(ttk.Frame):
    """Tab widget that provides verb conjugation practice."""

    def __init__(
        self,
        master: tk.Misc,
        exercise: ConjugationExercise,
        help_panel: PronunciationHelpPanel | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self._help_panel = help_panel
        self._tts_enabled = tts_available()
        self._answer_audio_ready = False
        self.title_var = tk.StringVar(value="Present-tense conjugation (beginner)")
        self.instructions_var = tk.StringVar(
            value="Type the present-tense verb form for the subject shown below. Type only the verb (for example: parle)."
        )
        self.phrase_var = tk.StringVar(value="")
        self.verb_var = tk.StringVar(value="")
        self.verb_ipa_var = tk.StringVar(value="")
        self.verb_phonetic_var = tk.StringVar(value="")
        self.pronoun_var = tk.StringVar(value="")
        self.pronoun_ipa_var = tk.StringVar(value="")
        self.pronoun_phonetic_var = tk.StringVar(value="")
        self.feedback_var = tk.StringVar(value="")
        self.answer_var = tk.StringVar(value="")

        self._build()

    def _build(self) -> None:
        ttk.Label(self, textvariable=self.title_var, font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(
            self,
            textvariable=self.instructions_var,
            font=("Helvetica", 11),
            foreground="gray40",
            wraplength=480,
            justify=tk.LEFT,
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 12))

        ttk.Label(self, text="Subject (pronoun):", font=("Helvetica", 12, "bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 2)
        )
        pron_frame = ttk.Frame(self)
        pron_frame.grid(row=2, column=1, columnspan=2, sticky="we")
        ttk.Label(pron_frame, textvariable=self.pronoun_var, font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")
        ttk.Label(
            pron_frame,
            textvariable=self.pronoun_ipa_var,
            font=("Helvetica", 11, "italic"),
            foreground="gray35",
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))
        ttk.Label(
            pron_frame,
            textvariable=self.pronoun_phonetic_var,
            font=("Helvetica", 11),
            foreground="gray45",
        ).grid(row=0, column=2, sticky="w", padx=(12, 0))

        ttk.Label(self, text="Verb (infinitive):", font=("Helvetica", 12, "bold")).grid(row=3, column=0, sticky="w")
        verb_frame = ttk.Frame(self)
        verb_frame.grid(row=3, column=1, columnspan=2, sticky="we")
        ttk.Label(verb_frame, textvariable=self.verb_var, font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")
        ttk.Label(
            verb_frame,
            textvariable=self.verb_ipa_var,
            font=("Helvetica", 11, "italic"),
            foreground="gray35",
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))
        ttk.Label(
            verb_frame,
            textvariable=self.verb_phonetic_var,
            font=("Helvetica", 11),
            foreground="gray45",
        ).grid(row=0, column=2, sticky="w", padx=(12, 0))

        ttk.Label(self, textvariable=self.phrase_var, font=("Helvetica", 16, "bold")).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(8, 6)
        )

        audio_frame = ttk.Frame(self)
        audio_frame.grid(row=5, column=0, columnspan=3, sticky="w")
        self.listen_infinitive_button = ttk.Button(
            audio_frame, text="Listen infinitive", command=self._listen_infinitive, state=tk.DISABLED
        )
        self.listen_infinitive_button.grid(row=0, column=0, padx=(0, 8))
        self.listen_answer_button = ttk.Button(
            audio_frame, text="Listen answer", command=self._listen_answer, state=tk.DISABLED
        )
        self.listen_answer_button.grid(row=0, column=1)
        self.listen_indicator = TTSStatusIndicator(audio_frame)
        self.listen_indicator.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        ttk.Label(self, text="Your answer (verb only):", font=("Helvetica", 12, "bold")).grid(
            row=8, column=0, sticky="w", pady=(10, 0)
        )
        answer_entry = ttk.Entry(self, textvariable=self.answer_var, width=24)
        answer_entry.grid(row=8, column=1, columnspan=2, sticky="we", pady=(10, 0))
        AccentToolbar(self, answer_entry, characters=("é", "è", "ê", "à")).grid(row=9, column=0, columnspan=3, sticky="w")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        ttk.Button(button_frame, text="Check", command=self._check).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(button_frame, text="Show answer", command=self._show_answer).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(button_frame, text="Previous pronoun", command=self._previous_pronoun).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(button_frame, text="Next pronoun", command=self._cycle_pronoun).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(button_frame, text="New verb", command=self._next).pack(side=tk.LEFT)

        ttk.Label(self, textvariable=self.feedback_var, foreground="seagreen").grid(
            row=11, column=0, columnspan=3, sticky="w", pady=(12, 0)
        )

        self.stats = StatsBar(self)
        self.stats.grid(row=12, column=0, columnspan=3, sticky="we", pady=(12, 0))

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self._refresh_audio_states()

    def _next(self) -> None:
        verb, pronoun = self.exercise.next_prompt()
        self._update_prompt(verb, pronoun)

    def _cycle_pronoun(self) -> None:
        verb, pronoun = self.exercise.cycle_prompt()
        self._update_prompt(verb, pronoun)

    def _update_prompt(self, verb: str, pronoun: str) -> None:
        pattern = self.exercise.current_pattern
        english_hint = ""
        if verb:
            if pattern and getattr(pattern, "english", ""):
                english_hint = f"{verb} - {pattern.english}"
            else:
                english_hint = verb
        self.verb_var.set(english_hint)

        pronoun_hints = {
            "je": "I",
            "tu": "you (singular)",
            "il/elle": "he/she",
            "nous": "we",
            "vous": "you (plural/formal)",
            "ils/elles": "they",
        }
        key = pronoun.lower() if pronoun else ""
        meaning = pronoun_hints.get(key, pronoun_hints.get(pronoun, ""))
        if pronoun and meaning:
            self.pronoun_var.set(f"{pronoun} ({meaning})")
        else:
            self.pronoun_var.set(pronoun)

        if pronoun and verb:
            phrase = f"{pronoun.capitalize()} ______ ({verb})"
        elif pronoun:
            phrase = f"{pronoun.capitalize()} ______"
        else:
            phrase = ""
        self.phrase_var.set(phrase)

        self._update_pronunciations(verb, pronoun)
        self.answer_var.set("")
        self.feedback_var.set("")
        self._answer_audio_ready = False
        self._refresh_audio_states()

    def _previous_pronoun(self) -> None:
        verb, pronoun = self.exercise.previous_prompt()
        self._update_prompt(verb, pronoun)

    def _check(self) -> None:
        if not self.answer_var.get().strip():
            self.feedback_var.set("Enter a conjugation first.")
            return
        correct = self.exercise.check_answer(self.answer_var.get())
        full_answer = self._current_full_answer()
        if correct:
            message = f"Correct: {full_answer}" if full_answer else "Correct!"
        else:
            message = f"Not quite. Correct answer: {full_answer}" if full_answer else "Not quite. Try again."
        self.feedback_var.set(message)
        self._answer_audio_ready = True
        self._refresh_audio_states()
        self._refresh_stats()

    def _current_full_answer(self) -> str | None:
        pattern = self.exercise.current_pattern
        if pattern is None:
            return None
        index = self.exercise.current_index
        if index < 0 or index >= len(pattern.pronouns) or index >= len(pattern.answers):
            return None
        pronoun = pattern.pronouns[index]
        answer = pattern.answers[index]
        if not pronoun or not answer:
            return None
        return f"{pronoun} {answer}"

    def _show_answer(self) -> None:
        if self.exercise.current_pattern is None:
            self.feedback_var.set("Click 'New verb' to get a question first.")
            return
        full_answer = self._current_full_answer()
        if full_answer:
            self.feedback_var.set(f"Answer: {full_answer}")
        else:
            self.feedback_var.set("Answer unavailable.")
        self._answer_audio_ready = True
        self._refresh_audio_states()

    def _refresh_stats(self) -> None:
        state = self.exercise.state
        self.stats.update_state(state.accuracy, state.current_streak)

    def _update_pronunciations(self, verb: str, pronoun: str) -> None:
        if verb:
            self.verb_ipa_var.set(to_ipa(verb))
            self.verb_phonetic_var.set(to_phonetic(verb))
        else:
            self.verb_ipa_var.set("")
            self.verb_phonetic_var.set("")

        if pronoun:
            pron_sources = {
                "je": "je",
                "tu": "tu",
                "il/elle": "il",
                "nous": "nous",
                "vous": "vous",
                "ils/elles": "ils",
            }
            base_pronoun = pron_sources.get(pronoun.lower(), pronoun)
        else:
            base_pronoun = ""

        if base_pronoun:
            self.pronoun_ipa_var.set(to_ipa(base_pronoun))
            self.pronoun_phonetic_var.set(to_phonetic(base_pronoun))
        else:
            self.pronoun_ipa_var.set("")
            self.pronoun_phonetic_var.set("")

        # Update side pronunciation help for the main verb phrase.
        if self._help_panel and verb:
            phrase = f"{base_pronoun} {verb}" if base_pronoun else verb
            explanation = explain_pronunciation(phrase.strip())
            self._help_panel.set_text(explanation)

    def _refresh_audio_states(self) -> None:
        verb_available = bool(self.exercise.current_pattern and self.exercise.current_pattern.infinitive)
        if not self._tts_enabled:
            self.listen_infinitive_button.state(["disabled"])
            self.listen_answer_button.state(["disabled"])
            return
        if verb_available:
            self.listen_infinitive_button.state(["!disabled"])
        else:
            self.listen_infinitive_button.state(["disabled"])
        if verb_available and self._answer_audio_ready:
            self.listen_answer_button.state(["!disabled"])
        else:
            self.listen_answer_button.state(["disabled"])

    def _listen_infinitive(self) -> None:
        if not self._tts_enabled:
            return
        pattern = self.exercise.current_pattern
        if not pattern:
            return
        _queue_tts_request(self, self.listen_indicator, pattern.infinitive)

    def _listen_answer(self) -> None:
        if not self._tts_enabled or not self._answer_audio_ready:
            return
        pattern = self.exercise.current_pattern
        if not pattern:
            return
        answer = pattern.answers[self.exercise.current_index]
        if not answer:
            return
        _queue_tts_request(self, self.listen_indicator, answer)


class SentencePracticeTab(ttk.Frame):
    """Tab displaying sentences along with IPA and learner-friendly phonetics."""

    def __init__(
        self,
        master: tk.Misc,
        exercise: SentencePracticeExercise,
        help_panel: PronunciationHelpPanel | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self._help_panel = help_panel
        self.category_var = tk.StringVar(value="all")
        self.use_generator_var = tk.BooleanVar(value=self.exercise.use_generator)
        self.sentence_var = tk.StringVar(value="Click New Sentence to begin")
        self.ipa_var = tk.StringVar()
        self.phonetic_var = tk.StringVar()
        self.translation_var = tk.StringVar(value="Translation hidden")
        self._current_translation = ""

        self._build()

    def _build(self) -> None:
        cat_values = category_values()
        ttk.Label(self, text="Category:").grid(row=0, column=0, sticky="w")
        ttk.OptionMenu(
            self, self.category_var, self.category_var.get(), *cat_values, command=self._change_category
        ).grid(row=0, column=1, sticky="w")

        ttk.Checkbutton(
            self,
            text="Use sentence generator",
            variable=self.use_generator_var,
            command=self._toggle_generator,
        ).grid(row=0, column=2, sticky="w", padx=(12, 0))

        ttk.Label(self, textvariable=self.sentence_var, font=("Helvetica", 18, "bold")).grid(
            row=1, column=0, columnspan=2, pady=(16, 4), sticky="w"
        )
        listen_state = tk.NORMAL if tts_available() else tk.DISABLED
        listen_frame = ttk.Frame(self)
        listen_frame.grid(row=1, column=2, sticky="ne")
        ttk.Button(listen_frame, text="Listen", command=self._listen_sentence, state=listen_state).grid(
            row=0, column=0, sticky="ew"
        )
        listen_frame.columnconfigure(0, weight=1)
        self.listen_indicator = TTSStatusIndicator(listen_frame)
        self.listen_indicator.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Label(self, textvariable=self.ipa_var, font=("Helvetica", 12, "italic"), foreground="gray25").grid(
            row=2, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(self, textvariable=self.phonetic_var, font=("Helvetica", 12), foreground="gray35").grid(
            row=3, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(self, textvariable=self.translation_var, font=("Helvetica", 12), foreground="slategray").grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(16, 0), sticky="w")
        ttk.Button(button_frame, text="New Sentence", command=self._next_sentence).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text="Reveal Translation", command=self._reveal_translation).pack(side=tk.LEFT)

        for i in range(3):
            self.columnconfigure(i, weight=1)

    def _change_category(self, category: str) -> None:
        self.exercise.set_category(category)
        self._next_sentence()

    def _toggle_generator(self) -> None:
        self.exercise.use_generator = self.use_generator_var.get()

    def _next_sentence(self) -> None:
        sentence = self.exercise.next_sentence()
        self.sentence_var.set(sentence.french)
        self.ipa_var.set(sentence.ipa)
        self.phonetic_var.set(sentence.phonetic)
        self._current_translation = sentence.english
        self.translation_var.set("Translation hidden")
        if self._help_panel:
            explanation = explain_pronunciation(sentence.french)
            self._help_panel.set_text(explanation)

    def _reveal_translation(self) -> None:
        if self._current_translation:
            self.translation_var.set(f"Translation: {self._current_translation}")

    def _listen_sentence(self) -> None:
        text = self.sentence_var.get()
        if text:
            _queue_tts_request(self, self.listen_indicator, text)


class FlipCardTab(ttk.Frame):
    """Flip-card memorization tab that toggles between front/back text."""

    def __init__(
        self,
        master: tk.Misc,
        exercise: FlipCardExercise,
        help_panel: PronunciationHelpPanel | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self._help_panel = help_panel
        self.category_var = tk.StringVar(value="all")
        self.language_label = language_label()
        self.side_var = tk.StringVar(value=f"Front ({self.language_label})")
        self.card_var = tk.StringVar(value="Press Next to start")
        self.translation_var = tk.StringVar()
        self.ipa_var = tk.StringVar()
        self.phonetic_var = tk.StringVar()

        self._build()

    def _build(self) -> None:
        cat_values = category_values()
        ttk.Label(self, text="Category:").grid(row=0, column=0, sticky="w")
        ttk.OptionMenu(
            self, self.category_var, self.category_var.get(), *cat_values, command=self._change_category
        ).grid(row=0, column=1, sticky="w")
        ttk.Button(self, text="Shuffle Deck", command=self._refresh).grid(row=0, column=2, sticky="e")

        ttk.Label(self, textvariable=self.side_var, font=("Helvetica", 12, "italic"), foreground="gray25").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )
        ttk.Label(self, textvariable=self.card_var, font=("Helvetica", 20, "bold")).grid(
            row=2, column=0, columnspan=2, sticky="we", pady=(8, 4)
        )
        listen_state = tk.NORMAL if tts_available() else tk.DISABLED
        listen_frame = ttk.Frame(self)
        listen_frame.grid(row=2, column=2, sticky="ne")
        ttk.Button(listen_frame, text="Listen", command=self._listen_card, state=listen_state).grid(
            row=0, column=0, sticky="ew"
        )
        listen_frame.columnconfigure(0, weight=1)
        self.listen_indicator = TTSStatusIndicator(listen_frame)
        self.listen_indicator.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Label(self, textvariable=self.translation_var, font=("Helvetica", 12), foreground="slategray").grid(
            row=3, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(self, textvariable=self.ipa_var, font=("Helvetica", 12, "italic"), foreground="gray25").grid(
            row=4, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(self, textvariable=self.phonetic_var, font=("Helvetica", 12), foreground="gray35").grid(
            row=5, column=0, columnspan=3, sticky="w"
        )

        button_frame = ttk.Frame(self)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(12, 0))
        ttk.Button(button_frame, text="Flip", command=self._flip).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="I knew this", command=lambda: self._mark_result(True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Didn't know", command=lambda: self._mark_result(False)).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="Next", command=self._next_card).pack(side=tk.LEFT, padx=2)

        self.stats = StatsBar(self)
        self.stats.grid(row=7, column=0, columnspan=3, sticky="we", pady=(12, 0))

        for i in range(3):
            self.columnconfigure(i, weight=1)

    def _change_category(self, category: str) -> None:
        self.exercise.set_category(category)
        self._next_card()

    def _refresh(self) -> None:
        self.exercise.refresh_deck()
        self._next_card()

    def _next_card(self) -> None:
        card = self.exercise.next_card()
        if card is None:
            self.side_var.set("No cards")
            self.card_var.set("No cards available for this category.")
            self.translation_var.set("")
            self.ipa_var.set("")
            self.phonetic_var.set("")
            return
        self._update_view(card)

    def _flip(self) -> None:
        card = self.exercise.flip()
        if card:
            self._update_view(card)

    def _update_view(self, card) -> None:
        if self.exercise.showing_front:
            self.side_var.set(f"Front ({self.language_label})")
            self.card_var.set(card.french)
            self.translation_var.set("Flip to reveal the English meaning.")
        else:
            self.side_var.set("Back (English)")
            self.card_var.set(card.english)
            self.translation_var.set(f"{self.language_label}: {card.french}")
        self.ipa_var.set(card.ipa)
        self.phonetic_var.set(card.phonetic)
        if self._help_panel:
            explanation = explain_pronunciation(card.french)
            self._help_panel.set_text(explanation)

    def _mark_result(self, knew: bool) -> None:
        self.exercise.mark_known(knew)
        self.stats.update_state(self.exercise.state.accuracy, self.exercise.state.current_streak)
        self._next_card()

    def _listen_card(self) -> None:
        card = self.exercise.current_card
        if card:
            _queue_tts_request(self, self.listen_indicator, card.french)


class LangPracticeApp(tk.Tk):
    """Main application window."""

    def __init__(self, registry: ExerciseRegistry | None = None) -> None:
        super().__init__()
        self.language_var = tk.StringVar(value=active_language_key())
        self.geometry("840x420")
        self.resizable(True, False)
        self.registry = registry or build_exercise_registry()
        self.container: ttk.Frame | None = None
        self.notebook: ttk.Notebook | None = None
        self.help_panel: PronunciationHelpPanel | None = None
        self._build_menu()
        self._apply_window_title()
        self._build_tabs()

    def _apply_window_title(self) -> None:
        language_label = get_active_module().label
        self.title(f"lang_practice - {language_label}")

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self)
        language_menu = tk.Menu(menu_bar, tearoff=False)
        for key, module in sorted(available_modules().items(), key=lambda item: item[1].label):
            language_menu.add_radiobutton(
                label=module.label,
                value=key,
                variable=self.language_var,
                command=lambda lang_key=key: self._switch_language(lang_key),
            )
        menu_bar.add_cascade(label="Language", menu=language_menu)
        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

    def _build_tabs(self) -> None:
        if self.container:
            self.container.destroy()

        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.container)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.help_panel = PronunciationHelpPanel(self.container)
        self.help_panel.grid(row=0, column=1, sticky="nsew")

        self.container.columnconfigure(0, weight=3)
        self.container.columnconfigure(1, weight=2)
        self.container.rowconfigure(0, weight=1)

        for name in self.registry.names():
            exercise = self.registry.create(name)
            if isinstance(exercise, FlashcardExercise):
                tab = FlashcardTab(self.notebook, exercise, self.help_panel)
            elif isinstance(exercise, SentencePracticeExercise):
                tab = SentencePracticeTab(self.notebook, exercise, self.help_panel)
            elif isinstance(exercise, FlipCardExercise):
                tab = FlipCardTab(self.notebook, exercise, self.help_panel)
            elif isinstance(exercise, ConjugationExercise):
                tab = ConjugationTab(self.notebook, exercise, self.help_panel)
            else:
                continue
            self.notebook.add(tab, text=name)

    def _switch_language(self, key: str) -> None:
        if key == active_language_key():
            return
        set_active_module(key)
        self.language_var.set(key)
        self.registry = build_exercise_registry()
        self._apply_window_title()
        self._build_tabs()

    def _show_about(self) -> None:
        language_label = get_active_module().label
        messagebox.showinfo(
            "About lang_practice",
            f"Practice {language_label} vocabulary and conjugations with a friendly GUI."
            "\nDeveloped as a modular example app.",
        )


def main() -> None:
    """Entry point used by ``python -m lang_practice``."""

    app = LangPracticeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
