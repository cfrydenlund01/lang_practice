"""Tkinter based GUI for modular language practice activities."""

from __future__ import annotations

import os
from pathlib import Path
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk
from dataclasses import dataclass, field
from random import sample
from typing import Callable

from .audio import play_audio
from .data import accented_characters, categories, present_tense_patterns, sentences, vocabulary_items
from .exercises import (
    ConjugationExercise,
    ExerciseRegistry,
    FlashcardExercise,
    FlipCardExercise,
    SentencePracticeExercise,
    answer_matches,
    build_exercise_registry,
)
from .language_registry import active_language_key, available_modules, get_active_module, set_active_module
from .models import VocabularyItem
from .pronunciation import explain_pronunciation, to_ipa, to_phonetic
from .review_db import ReviewDB, ReviewItem
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


@dataclass
class SessionMetrics:
    started_monotonic: float = field(default_factory=time.monotonic)
    total_attempts: int = 0
    correct_attempts: int = 0

    def register_attempt(self, correct: bool) -> None:
        self.total_attempts += 1
        if correct:
            self.correct_attempts += 1

    @property
    def duration_seconds(self) -> int:
        return max(0, int(time.monotonic() - self.started_monotonic))

    def format_duration(self) -> str:
        seconds = self.duration_seconds
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:d}:{minutes:02d}:{sec:02d}"
        return f"{minutes:d}:{sec:02d}"

    def format_accuracy(self) -> str:
        if self.total_attempts == 0:
            return "0/0 (0%)"
        pct = int(round((self.correct_attempts / self.total_attempts) * 100))
        return f"{self.correct_attempts}/{self.total_attempts} ({pct}%)"


class SessionFooter(ttk.Frame):
    def __init__(self, master: tk.Misc, metrics: SessionMetrics) -> None:
        super().__init__(master, padding=(10, 6))
        self.metrics = metrics
        self.time_var = tk.StringVar(value="0:00")
        self.accuracy_var = tk.StringVar(value="0%")

        base_font = tkfont.nametofont("TkDefaultFont")
        display_font = base_font.copy()
        display_font.configure(size=14)

        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, pady=(0, 6))
        content = ttk.Frame(self)
        content.pack(fill=tk.X)
        ttk.Label(content, textvariable=self.time_var, font=display_font).grid(row=0, column=0, sticky="w")
        ttk.Label(content, textvariable=self.accuracy_var, font=display_font).grid(row=0, column=1, sticky="e")
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

    def refresh(self) -> None:
        self.time_var.set(self.metrics.format_duration())
        total = self.metrics.total_attempts
        if total == 0:
            pct = 0
        else:
            pct = int(round((self.metrics.correct_attempts / total) * 100))
        self.accuracy_var.set(f"{pct}%")


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
    """Side panel showing the lesson or guide for the active exercise."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=(8, 8))
        self.title_var = tk.StringVar(value="Pronunciation guide")
        ttk.Label(self, textvariable=self.title_var, font=("Helvetica", 11, "bold")).grid(
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
        self.title_var.set("Pronunciation guide")
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")

    def set_content(self, title: str, content: str) -> None:
        self.set_text(content)
        self.title_var.set(title)


def _queue_tts_request(widget: tk.Misc, indicator: TTSStatusIndicator, text: str, *, lang: str | None = None) -> None:
    """Trigger a TTS request while updating an indicator from the Tk thread."""

    if not text:
        return

    def _start() -> None:
        widget.after(0, indicator.start)

    def _finish(success: bool) -> None:
        widget.after(0, indicator.finish, success)

    play_tts_async(text, lang=lang, on_start=_start, on_complete=_finish)


def _install_arrow_key_focus_traversal(widgets: list[tk.Widget]) -> None:
    if not widgets:
        return

    def _is_focusable(widget: tk.Widget) -> bool:
        if not widget.winfo_viewable():
            return False
        if hasattr(widget, "instate"):
            try:
                return not widget.instate(["disabled"])
            except tk.TclError:
                return True
        try:
            return str(widget.cget("state")) not in {"disabled", "0"}
        except tk.TclError:
            return True

    def _next(current: tk.Widget, delta: int) -> None:
        if not widgets:
            return
        try:
            index = widgets.index(current)
        except ValueError:
            index = 0
        size = len(widgets)
        for offset in range(1, size + 1):
            candidate = widgets[(index + delta * offset) % size]
            if _is_focusable(candidate):
                candidate.focus_set()
                break

    for widget in widgets:
        widget.bind("<Left>", lambda event, w=widget: (_next(w, -1), "break")[1])
        widget.bind("<Up>", lambda event, w=widget: (_next(w, -1), "break")[1])
        widget.bind("<Right>", lambda event, w=widget: (_next(w, 1), "break")[1])
        widget.bind("<Down>", lambda event, w=widget: (_next(w, 1), "break")[1])


class KeyboardNavigableTab(ttk.Frame):
    def __init__(self, master: tk.Misc, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._default_button: ttk.Button | None = None
        self._action_buttons: list[ttk.Button] = []
        self._enter_target_button: ttk.Button | None = None
        self._base_styles: dict[str, str] = {}

    def set_default_button(self, button: ttk.Button) -> None:
        self._default_button = button
        button.configure(takefocus=True)

    def register_action_buttons(self, buttons: list[ttk.Button]) -> None:
        self._action_buttons = [*buttons]
        for button in self._action_buttons:
            self._base_styles.setdefault(str(button), str(button.cget("style") or ""))
            button.configure(takefocus=True)
        _install_arrow_key_focus_traversal([*buttons])

    def focus_default_button(self) -> None:
        if self._default_button and not self._default_button.instate(["disabled"]):
            self._default_button.focus_set()

    def invoke_default_button(self) -> bool:
        if not self._default_button or self._default_button.instate(["disabled"]):
            return False
        self._default_button.invoke()
        return True

    def update_enter_target(self, focus_widget: tk.Misc | None) -> None:
        target: ttk.Button | None = None
        if isinstance(focus_widget, ttk.Button) and focus_widget in self._action_buttons:
            if not focus_widget.instate(["disabled"]):
                target = focus_widget
        if target is None:
            if self._default_button and not self._default_button.instate(["disabled"]):
                target = self._default_button
            else:
                for button in self._action_buttons:
                    if not button.instate(["disabled"]):
                        target = button
                        break
        self._set_enter_target_button(target)

    def _set_enter_target_button(self, button: ttk.Button | None) -> None:
        if button is self._enter_target_button:
            return
        if self._enter_target_button and self._enter_target_button.winfo_exists():
            base_style = self._base_styles.get(str(self._enter_target_button), "")
            self._enter_target_button.configure(style=base_style)
        self._enter_target_button = button
        if self._enter_target_button and self._enter_target_button.winfo_exists():
            self._enter_target_button.configure(style="EnterTarget.TButton")

    def invoke_focused_or_default(self, focus_widget: tk.Misc | None) -> bool:
        if focus_widget and hasattr(focus_widget, "invoke") and isinstance(focus_widget, (ttk.Button, tk.Button)):
            try:
                focus_widget.invoke()
                return True
            except tk.TclError:
                return False
        return self.invoke_default_button()


class ScrollableTabHost(ttk.Frame):
    """Give each exercise a vertical scrollbar when its controls exceed the window."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.content: KeyboardNavigableTab | None = None
        self._window_id: int | None = None
        self.canvas.bind("<Configure>", self._fit_content_width)

    def set_content(self, content: KeyboardNavigableTab) -> None:
        self.content = content
        self._window_id = self.canvas.create_window((0, 0), anchor="nw", window=content)
        content.bind("<Configure>", self._refresh_scroll_region, add="+")
        self._refresh_scroll_region()

    def _refresh_scroll_region(self, event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _fit_content_width(self, event) -> None:
        if self._window_id is not None:
            self.canvas.itemconfigure(self._window_id, width=event.width)
        self._refresh_scroll_region()


class FlashcardTab(KeyboardNavigableTab):
    """Tab widget that wires the flashcard exercise into the UI."""

    def __init__(
        self,
        master: tk.Misc,
        exercise: FlashcardExercise,
        on_attempt: Callable[[bool, str | None, str | None, str | None], None],
        help_panel: PronunciationHelpPanel | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self._on_attempt = on_attempt
        self._help_panel = help_panel
        self.prompt_var = tk.StringVar(value="Press Next to start")
        self.ipa_var = tk.StringVar()
        self.phonetic_var = tk.StringVar()
        self.feedback_var = tk.StringVar()
        self.answer_var = tk.StringVar()
        self.category_var = tk.StringVar(value="all")

        self._build()
        self._revealed_this_item = False

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
        self.listen_button = ttk.Button(listen_frame, text="Listen", command=self._play_audio, state=listen_state)
        self.listen_button.grid(
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
        self.check_button = ttk.Button(button_frame, text="Check", command=self._check_answer)
        self.check_button.pack(fill=tk.X, pady=2)
        self.reveal_button = ttk.Button(button_frame, text="Reveal", command=self._reveal_answer)
        self.reveal_button.pack(fill=tk.X, pady=2)
        self.prev_button = ttk.Button(button_frame, text="Previous", command=self._previous, state=tk.DISABLED)
        self.prev_button.pack(fill=tk.X, pady=2)
        self.next_button = ttk.Button(button_frame, text="Next", command=self._next)
        self.next_button.pack(fill=tk.X, pady=2)

        self.set_default_button(self.check_button)
        self.register_action_buttons(
            [self.listen_button, self.check_button, self.reveal_button, self.prev_button, self.next_button]
        )
        self.update_enter_target(None)

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
        self._revealed_this_item = False
        self._update_previous_state()
        self._update_help(item.french)

    def _update_previous_state(self) -> None:
        state = tk.NORMAL if self.exercise.has_previous() else tk.DISABLED
        self.prev_button.configure(state=state)

    def _check_answer(self) -> None:
        if not self.answer_var.get():
            self.feedback_var.set("Type your answer first.")
            return
        answer = self.answer_var.get()
        correct = self.exercise.check_answer(answer)
        current = self.exercise.current_item
        if current:
            prompt = current.french
            correct_answer = current.english
            self._on_attempt(correct, prompt, correct_answer, answer)
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
            if not self._revealed_this_item:
                item = self.exercise.current_item
                self._on_attempt(False, item.french, item.english, "")
                self._revealed_this_item = True

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



class ConjugationTab(KeyboardNavigableTab):
    """Tab widget that provides verb conjugation practice."""

    def __init__(
        self,
        master: tk.Misc,
        exercise: ConjugationExercise,
        on_attempt: Callable[[bool, str | None, str | None, str | None], None],
        help_panel: PronunciationHelpPanel | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self._on_attempt = on_attempt
        self._help_panel = help_panel
        self._tts_enabled = tts_available()
        self._answer_audio_ready = False
        self._started = False
        self._lesson_visible = False
        self.title_var = tk.StringVar(value=f"{language_label()} present-tense conjugation")
        self.instructions_var = tk.StringVar(
            value="Start practice to choose a verb. You can open the lesson table at any time."
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
        self._attempted_current_prompt = False

    def _build(self) -> None:
        ttk.Label(self, textvariable=self.title_var, font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        self.instructions_label = ttk.Label(
            self,
            textvariable=self.instructions_var,
            font=("Helvetica", 11),
            foreground="gray40",
            wraplength=480,
            justify=tk.LEFT,
        )
        self.instructions_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 12))

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

        self.lesson_button = ttk.Button(self, text="Show lesson", command=self._toggle_lesson, state=tk.DISABLED)
        self.lesson_button.grid(row=6, column=0, sticky="w", pady=(8, 0))
        self.lesson_frame = ttk.LabelFrame(self, text="Learn this verb", padding=(8, 6))
        self.lesson_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        self.lesson_table = ttk.Treeview(self.lesson_frame, columns=("pronoun", "form"), show="headings", height=6)
        self.lesson_table.heading("pronoun", text="Subject")
        self.lesson_table.heading("form", text="Present form")
        self.lesson_table.column("pronoun", width=150, stretch=True)
        self.lesson_table.column("form", width=180, stretch=True)
        self.lesson_table.grid(row=0, column=0, sticky="ew")
        self.lesson_frame.columnconfigure(0, weight=1)
        self.lesson_frame.grid_remove()

        ttk.Label(self, text="Your answer (verb only):", font=("Helvetica", 12, "bold")).grid(
            row=8, column=0, sticky="w", pady=(10, 0)
        )
        answer_entry = ttk.Entry(self, textvariable=self.answer_var, width=24)
        answer_entry.grid(row=8, column=1, columnspan=2, sticky="we", pady=(10, 0))
        AccentToolbar(self, answer_entry).grid(row=9, column=0, columnspan=3, sticky="w")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        self.check_button = ttk.Button(button_frame, text="Check", command=self._check, state=tk.DISABLED)
        self.check_button.pack(side=tk.LEFT, padx=(0, 6))
        self.show_answer_button = ttk.Button(button_frame, text="Show answer", command=self._show_answer, state=tk.DISABLED)
        self.show_answer_button.pack(side=tk.LEFT, padx=(0, 6))
        self.previous_pronoun_button = ttk.Button(button_frame, text="Previous pronoun", command=self._previous_pronoun, state=tk.DISABLED)
        self.previous_pronoun_button.pack(side=tk.LEFT, padx=(0, 6))
        self.next_pronoun_button = ttk.Button(button_frame, text="Next pronoun", command=self._cycle_pronoun, state=tk.DISABLED)
        self.next_pronoun_button.pack(side=tk.LEFT, padx=(0, 6))
        self.next_button = ttk.Button(button_frame, text="Start practice", command=self._start_practice)
        self.next_button.pack(side=tk.LEFT)

        self.set_default_button(self.next_button)
        self.register_action_buttons(
            [
                self.listen_infinitive_button,
                self.listen_answer_button,
                self.check_button,
                self.show_answer_button,
                self.previous_pronoun_button,
                self.next_pronoun_button,
                self.next_button,
            ]
        )
        self.update_enter_target(None)

        ttk.Label(self, textvariable=self.feedback_var, foreground="seagreen").grid(
            row=11, column=0, columnspan=3, sticky="w", pady=(12, 0)
        )

        self.stats = StatsBar(self)
        self.stats.grid(row=12, column=0, columnspan=3, sticky="we", pady=(12, 0))

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.bind("<Configure>", self._resize_wrapped_content, add="+")
        self._refresh_audio_states()

    def _start_practice(self) -> None:
        self._started = True
        self.next_button.configure(text="New verb")
        for button in (
            self.check_button,
            self.show_answer_button,
            self.previous_pronoun_button,
            self.next_pronoun_button,
            self.lesson_button,
        ):
            button.state(["!disabled"])
        self._next()

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

        pronoun_hints = self._pronoun_hints()
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
        self._populate_lesson()
        self.answer_var.set("")
        self.feedback_var.set("")
        self._answer_audio_ready = False
        self._attempted_current_prompt = False
        self._refresh_audio_states()

    def _pronoun_hints(self) -> dict[str, str]:
        by_language = {
            "french": {
                "je": "I",
                "tu": "you (singular)",
                "il/elle": "he/she",
                "nous": "we",
                "vous": "you (plural/formal)",
                "ils/elles": "they",
            },
            "italian": {
                "io": "I",
                "tu": "you (singular)",
                "lui/lei": "he/she",
                "noi": "we",
                "voi": "you (plural/formal)",
                "loro": "they",
            },
        }
        return by_language.get(active_language_key(), {})

    def _populate_lesson(self) -> None:
        for item in self.lesson_table.get_children():
            self.lesson_table.delete(item)
        pattern = self.exercise.current_pattern
        if not pattern:
            return
        for pronoun, form in zip(pattern.pronouns, pattern.answers):
            self.lesson_table.insert("", tk.END, values=(pronoun, form))
        if self._help_panel and self._lesson_visible:
            lesson = get_active_module().explain_conjugation(pattern)
            self._help_panel.set_content(f"Conjugation lesson: {pattern.infinitive}", lesson)

    def show_help(self) -> None:
        """Show this tab's lesson in the shared right-hand panel."""

        if not self._help_panel:
            return
        pattern = self.exercise.current_pattern
        if self._lesson_visible and pattern:
            lesson = get_active_module().explain_conjugation(pattern)
            self._help_panel.set_content(f"Conjugation lesson: {pattern.infinitive}", lesson)
            return
        self._show_hidden_lesson_state()

    def _toggle_lesson(self) -> None:
        self._show_lesson(not self._lesson_visible)

    def _show_lesson(self, visible: bool) -> None:
        self._lesson_visible = visible
        if visible:
            self.lesson_frame.grid()
            self.lesson_button.configure(text="Hide lesson")
            pattern = self.exercise.current_pattern
            if self._help_panel and pattern:
                lesson = get_active_module().explain_conjugation(pattern)
                self._help_panel.set_content(f"Conjugation lesson: {pattern.infinitive}", lesson)
        else:
            self.lesson_frame.grid_remove()
            self.lesson_button.configure(text="Show lesson")
            self._show_hidden_lesson_state()

    def _resize_wrapped_content(self, event=None) -> None:
        width = max(320, self.winfo_width() - 40)
        self.instructions_label.configure(wraplength=width)

    def _previous_pronoun(self) -> None:
        verb, pronoun = self.exercise.previous_prompt()
        self._update_prompt(verb, pronoun)

    def _check(self) -> None:
        if not self.answer_var.get().strip():
            self.feedback_var.set("Enter a conjugation first.")
            return
        answer = self.answer_var.get()
        correct = self.exercise.check_answer(answer)
        full_answer = self._current_full_answer()
        if full_answer:
            prompt = self.phrase_var.get().strip() or self.verb_var.get().strip()
            self._on_attempt(correct, prompt, full_answer, answer)
            self._attempted_current_prompt = True
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
            self.feedback_var.set("Click 'Start practice' to get a question first.")
            return
        full_answer = self._current_full_answer()
        if full_answer:
            self.feedback_var.set(f"Answer: {full_answer}")
            if not self._attempted_current_prompt:
                prompt = self.phrase_var.get().strip() or self.verb_var.get().strip()
                self._on_attempt(False, prompt, full_answer, self.answer_var.get())
                self._attempted_current_prompt = True
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
            base_pronoun = pronoun.split("/")[0].strip()
        else:
            base_pronoun = ""

        if base_pronoun:
            self.pronoun_ipa_var.set(to_ipa(base_pronoun))
            self.pronoun_phonetic_var.set(to_phonetic(base_pronoun))
        else:
            self.pronoun_ipa_var.set("")
            self.pronoun_phonetic_var.set("")

        if not self._lesson_visible:
            self._show_hidden_lesson_state()

    def _show_hidden_lesson_state(self) -> None:
        """Keep the conjugation panel empty of lesson content until requested."""

        if not self._help_panel:
            return
        self._help_panel.set_content(
            "Conjugation lesson",
            "Lesson hidden. Select Show lesson when you want conjugation instructions.",
        )


    def _refresh_audio_states(self) -> None:
        verb_available = self._started and bool(self.exercise.current_pattern and self.exercise.current_pattern.infinitive)
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
        answer = self._current_full_answer()
        if not answer:
            return
        _queue_tts_request(self, self.listen_indicator, answer)


class SentencePracticeTab(KeyboardNavigableTab):
    """Tab displaying sentences along with IPA and learner-friendly phonetics."""

    def __init__(
        self,
        master: tk.Misc,
        exercise: SentencePracticeExercise,
        on_attempt: Callable[[bool, str | None, str | None, str | None], None],
        help_panel: PronunciationHelpPanel | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self._on_attempt = on_attempt
        self._help_panel = help_panel
        self.category_var = tk.StringVar(value="all")
        self.use_generator_var = tk.BooleanVar(value=self.exercise.use_generator)
        self.sentence_var = tk.StringVar(value="Click New Sentence to begin")
        self.ipa_var = tk.StringVar()
        self.phonetic_var = tk.StringVar()
        self.translation_var = tk.StringVar(value="Translation hidden")
        self.feedback_var = tk.StringVar(value="")
        self.answer_var = tk.StringVar(value="")
        self._current_translation = ""
        self._current_prompt = ""
        self._revealed_current = False
        self._history = []
        self._history_index = -1

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
        self.listen_button = ttk.Button(listen_frame, text="Listen", command=self._listen_sentence, state=listen_state)
        self.listen_button.grid(row=0, column=0, sticky="ew")
        listen_frame.columnconfigure(0, weight=1)
        self.listen_indicator = TTSStatusIndicator(listen_frame)
        self.listen_indicator.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Label(self, textvariable=self.ipa_var, font=("Helvetica", 12, "italic"), foreground="gray25").grid(
            row=2, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(self, textvariable=self.phonetic_var, font=("Helvetica", 12), foreground="gray35").grid(
            row=3, column=0, columnspan=3, sticky="w"
        )

        answer_entry = ttk.Entry(self, textvariable=self.answer_var, width=34)
        answer_entry.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="we")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=2, rowspan=2, padx=(8, 0), pady=(10, 0), sticky="ns")
        self.check_button = ttk.Button(button_frame, text="Check", command=self._check_answer, state=tk.DISABLED)
        self.check_button.pack(fill=tk.X, pady=2)
        self.reveal_button = ttk.Button(
            button_frame, text="Reveal", command=self._reveal_translation, state=tk.DISABLED
        )
        self.reveal_button.pack(fill=tk.X, pady=2)
        self.prev_button = ttk.Button(button_frame, text="Previous", command=self._previous_sentence, state=tk.DISABLED)
        self.prev_button.pack(fill=tk.X, pady=2)
        self.next_button = ttk.Button(button_frame, text="New Sentence", command=self._next_sentence)
        self.next_button.pack(fill=tk.X, pady=2)

        ttk.Label(self, textvariable=self.translation_var, font=("Helvetica", 12), foreground="slategray").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        ttk.Label(self, textvariable=self.feedback_var, foreground="steelblue").grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

        self.set_default_button(self.check_button)
        self.register_action_buttons(
            [self.listen_button, self.check_button, self.reveal_button, self.prev_button, self.next_button]
        )
        self.update_enter_target(None)

        for i in range(3):
            self.columnconfigure(i, weight=1)

    def _change_category(self, category: str) -> None:
        self.exercise.set_category(category)
        self._reset_history()
        self._next_sentence()

    def _toggle_generator(self) -> None:
        self.exercise.use_generator = self.use_generator_var.get()

    def _next_sentence(self) -> None:
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            sentence = self._history[self._history_index]
        else:
            sentence = self.exercise.next_sentence()
            self._history.append(sentence)
            self._history_index = len(self._history) - 1
        self._load_sentence(sentence)

    def _previous_sentence(self) -> None:
        if self._history_index <= 0:
            return
        self._history_index -= 1
        sentence = self._history[self._history_index]
        self._load_sentence(sentence)

    def _load_sentence(self, sentence) -> None:
        self._current_prompt = sentence.french
        self.sentence_var.set(sentence.french)
        self.ipa_var.set(sentence.ipa)
        self.phonetic_var.set(sentence.phonetic)
        self._current_translation = sentence.english
        self.translation_var.set("Translation hidden")
        self.feedback_var.set("")
        self.answer_var.set("")
        self._revealed_current = False
        self.check_button.state(["!disabled"])
        self.reveal_button.state(["!disabled"])
        if self._history_index > 0:
            self.prev_button.state(["!disabled"])
        else:
            self.prev_button.state(["disabled"])
        self.update_enter_target(self.focus_get())
        if self._help_panel:
            explanation = explain_pronunciation(sentence.french)
            self._help_panel.set_text(explanation)

    def _reset_history(self) -> None:
        self._history = []
        self._history_index = -1
        self._current_translation = ""
        self._current_prompt = ""
        self.translation_var.set("Translation hidden")
        self.feedback_var.set("")
        self.answer_var.set("")
        self.check_button.state(["disabled"])
        self.reveal_button.state(["disabled"])
        self.prev_button.state(["disabled"])
        self.update_enter_target(self.focus_get())

    def _reveal_translation(self) -> None:
        if self._current_translation:
            self.translation_var.set(f"Translation: {self._current_translation}")
            if not self._revealed_current and self._current_prompt:
                self._on_attempt(False, self._current_prompt, self._current_translation, self.answer_var.get())
                self._revealed_current = True

    def _check_answer(self) -> None:
        if not self._current_translation or not self._current_prompt:
            self.feedback_var.set("Click New Sentence to begin.")
            return
        answer = self.answer_var.get()
        if not answer.strip():
            self.feedback_var.set("Type your answer first.")
            return
        correct = answer_matches(answer, self._current_translation)
        self._on_attempt(correct, self._current_prompt, self._current_translation, answer)
        if correct:
            self.feedback_var.set("Correct!")
            self._next_sentence()
        else:
            self.feedback_var.set(f"Not quite. Answer: {self._current_translation}")

    def _listen_sentence(self) -> None:
        text = self.sentence_var.get()
        if text:
            _queue_tts_request(self, self.listen_indicator, text)


class FlipCardTab(KeyboardNavigableTab):
    """Flip-card memorization tab that toggles between front/back text."""

    def __init__(
        self,
        master: tk.Misc,
        exercise: FlipCardExercise,
        on_attempt: Callable[[bool, str | None, str | None, str | None], None],
        help_panel: PronunciationHelpPanel | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self.exercise = exercise
        self._on_attempt = on_attempt
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
        self.listen_button = ttk.Button(listen_frame, text="Listen", command=self._listen_card, state=listen_state)
        self.listen_button.grid(row=0, column=0, sticky="ew")
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
        self.flip_button = ttk.Button(button_frame, text="Flip", command=self._flip)
        self.flip_button.pack(side=tk.LEFT, padx=2)
        self.knew_button = ttk.Button(button_frame, text="I knew this", command=lambda: self._mark_result(True))
        self.knew_button.pack(side=tk.LEFT, padx=2)
        self.didnt_know_button = ttk.Button(button_frame, text="Didn't know", command=lambda: self._mark_result(False))
        self.didnt_know_button.pack(side=tk.LEFT, padx=2)
        self.next_button = ttk.Button(button_frame, text="Next", command=self._next_card)
        self.next_button.pack(side=tk.LEFT, padx=2)

        self.set_default_button(self.next_button)
        self.register_action_buttons(
            [
                self.listen_button,
                self.flip_button,
                self.knew_button,
                self.didnt_know_button,
                self.next_button,
            ]
        )
        self.update_enter_target(None)

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
        card = self.exercise.current_card
        if card and not knew:
            self._on_attempt(False, card.french, card.english, "")
        elif card and knew:
            self._on_attempt(True, card.french, card.english, "")
        self.stats.update_state(self.exercise.state.accuracy, self.exercise.state.current_streak)
        self._next_card()

    def _listen_card(self) -> None:
        card = self.exercise.current_card
        if card:
            _queue_tts_request(self, self.listen_indicator, card.french)


class ReviewTab(KeyboardNavigableTab):
    """Multiple-choice review tab based on wrong/missed answers from the previous session."""

    def __init__(
        self,
        master: tk.Misc,
        items: list[ReviewItem],
        on_attempt: Callable[[bool, str | None, str | None, str | None], None],
    ) -> None:
        super().__init__(master, padding=12)
        self._items = items
        self._on_attempt = on_attempt
        self._index = 0

        self.title_var = tk.StringVar(value="Review")
        self.prompt_var = tk.StringVar(value="")
        self.feedback_var = tk.StringVar(value="")
        self.selected_var = tk.StringVar(value="")

        self._options_frame: ttk.Frame | None = None
        self._option_buttons: list[ttk.Radiobutton] = []
        self._translation_pool = self._build_translation_pool()
        self._conjugation_pool = self._build_conjugation_pool()

        self._build()
        self._load_current()

    def refresh_items(self, items: list[ReviewItem]) -> None:
        """Reload due cards when the learner enters Review during this session."""

        self._items = items
        self._index = 0
        self._load_current()

    def _build_translation_pool(self) -> list[str]:
        pool = [item.english for item in vocabulary_items()]
        pool.extend(sentence.english for sentence in sentences())
        return [value for value in pool if value]

    def _build_conjugation_pool(self) -> list[str]:
        pool: list[str] = []
        for pattern in present_tense_patterns():
            for pronoun, answer in zip(pattern.pronouns, pattern.answers):
                if pronoun and answer:
                    pool.append(f"{pronoun} {answer}")
        return pool

    def _build(self) -> None:
        ttk.Label(self, textvariable=self.title_var, font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(self, textvariable=self.prompt_var, font=("Helvetica", 16, "bold"), wraplength=520).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(10, 10)
        )

        self._options_frame = ttk.Frame(self)
        self._options_frame.grid(row=2, column=0, columnspan=2, sticky="w")

        self.check_button = ttk.Button(self, text="Check", command=self._check)
        self.check_button.grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.set_default_button(self.check_button)
        self.register_action_buttons([self.check_button])
        self.update_enter_target(None)

        ttk.Label(self, textvariable=self.feedback_var, foreground="steelblue").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(10, 0)
        )

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def _load_current(self) -> None:
        if not self._items:
            self.prompt_var.set("No review items are due. Practice normally and missed items will appear here immediately.")
            self.feedback_var.set("")
            self.check_button.state(["disabled"])
            return
        if self._index >= len(self._items):
            self.prompt_var.set("Review complete for this session.")
            self.feedback_var.set("")
            self.check_button.state(["disabled"])
            return

        item = self._items[self._index]
        self.feedback_var.set("")
        self.selected_var.set("")
        self.check_button.state(["!disabled"])
        self.prompt_var.set(f"{item.exercise}: {item.prompt}")

        options = self._build_options(item)
        self._render_options(options)

    def _build_options(self, item: ReviewItem) -> list[str]:
        correct = item.correct_answer
        pool = self._conjugation_pool if correct in self._conjugation_pool else self._translation_pool
        candidates = [value for value in pool if value and value != correct]
        distractors = sample(candidates, k=min(3, len(candidates))) if candidates else []
        options = [correct, *distractors]
        # Ensure uniqueness and stable order while keeping correct present.
        seen: set[str] = set()
        unique: list[str] = []
        for value in options:
            if value and value not in seen:
                unique.append(value)
                seen.add(value)
        return sample(unique, k=len(unique)) if len(unique) > 1 else unique

    def _render_options(self, options: list[str]) -> None:
        assert self._options_frame is not None
        for widget in self._options_frame.winfo_children():
            widget.destroy()
        self._option_buttons.clear()

        for idx, option in enumerate(options):
            btn = ttk.Radiobutton(self._options_frame, text=option, value=option, variable=self.selected_var)
            btn.grid(row=idx, column=0, sticky="w", pady=2)
            self._option_buttons.append(btn)

    def _check(self) -> None:
        if not self._items or self._index >= len(self._items):
            return
        item = self._items[self._index]
        choice = self.selected_var.get()
        if not choice:
            self.feedback_var.set("Pick an answer first.")
            return
        correct = choice == item.correct_answer
        self._on_attempt(correct, item.prompt, item.correct_answer, choice, item.exercise)
        self.feedback_var.set("Correct!" if correct else f"Not quite. Correct answer: {item.correct_answer}")
        self._index += 1
        self.after(650, self._load_current)


class LangPracticeApp(tk.Tk):
    """Main application window."""

    def __init__(self, registry: ExerciseRegistry | None = None) -> None:
        super().__init__()
        self.session_metrics = SessionMetrics()
        self._session_timer_job: str | None = None
        project_root = Path(__file__).resolve().parent.parent
        self.review_db = ReviewDB(project_root / "cache" / "review.sqlite3")
        self.session_id = self.review_db.start_session()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.language_var = tk.StringVar(value=active_language_key())
        self.geometry("1080x720")
        self.minsize(760, 520)
        self.resizable(True, True)
        self._install_styles()
        self.registry = registry or build_exercise_registry()
        self.container: ttk.Frame | None = None
        self.notebook: ttk.Notebook | None = None
        self.help_panel: PronunciationHelpPanel | None = None
        self._build_menu()
        self._apply_window_title()
        self._build_tabs()
        self._install_keyboard_shortcuts()
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed, add="+")
        self.after(0, self._on_tab_changed)
        self._start_session_timer()

    def _install_styles(self) -> None:
        style = ttk.Style(self)
        base_font = tkfont.nametofont("TkDefaultFont")
        bold_font = base_font.copy()
        bold_font.configure(weight="bold")
        style.configure("EnterTarget.TButton", font=bold_font)

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
        self.guide_toggle_button = ttk.Button(self.container, text="Hide guide", command=self._toggle_help_panel)
        self.guide_toggle_button.grid(row=1, column=1, sticky="ne", padx=8, pady=(0, 6))

        self.session_footer = SessionFooter(self.container, self.session_metrics)
        self.session_footer.grid(row=1, column=0, sticky="ew")
        self.session_footer.refresh()

        self.container.columnconfigure(0, weight=3)
        self.container.columnconfigure(1, weight=2)
        self.container.rowconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=0)

        for name in self.registry.names():
            exercise = self.registry.create(name)
            host = ScrollableTabHost(self.notebook)
            if isinstance(exercise, FlashcardExercise):
                tab = FlashcardTab(host.canvas, exercise, self._on_attempt, self.help_panel)
            elif isinstance(exercise, SentencePracticeExercise):
                tab = SentencePracticeTab(host.canvas, exercise, self._on_attempt, self.help_panel)
            elif isinstance(exercise, FlipCardExercise):
                tab = FlipCardTab(host.canvas, exercise, self._on_attempt, self.help_panel)
            elif isinstance(exercise, ConjugationExercise):
                tab = ConjugationTab(host.canvas, exercise, self._on_attempt, self.help_panel)
            else:
                continue
            host.set_content(tab)
            self.notebook.add(host, text=name)

        review_items = self._load_review_items()
        review_host = ScrollableTabHost(self.notebook)
        review_tab = ReviewTab(review_host.canvas, review_items, self._on_attempt)
        review_host.set_content(review_tab)
        self.notebook.add(review_host, text="Review")

    def _load_review_items(self) -> list[ReviewItem]:
        return self.review_db.due_items(language=active_language_key())

    def _on_attempt(
        self,
        correct: bool,
        prompt: str | None,
        correct_answer: str | None,
        user_answer: str | None,
        exercise_name: str | None = None,
    ) -> None:
        self.session_metrics.register_attempt(correct)
        if prompt and correct_answer is not None and user_answer is not None:
            self.review_db.record_attempt(
                language=active_language_key(),
                exercise=exercise_name or self._active_exercise_name(),
                prompt=prompt,
                correct_answer=correct_answer,
                user_answer=user_answer,
                correct=correct,
            )
        if getattr(self, "session_footer", None):
            self.session_footer.refresh()

    def _active_exercise_name(self) -> str:
        if not self.notebook:
            return "Unknown"
        selected = self.notebook.select()
        if not selected:
            return "Unknown"
        try:
            text = self.notebook.tab(selected, "text")
        except tk.TclError:
            return "Unknown"
        return str(text) if text else "Unknown"

    def _start_session_timer(self) -> None:
        def _tick() -> None:
            if getattr(self, "session_footer", None):
                self.session_footer.refresh()
            self._session_timer_job = self.after(1000, _tick)

        if self._session_timer_job:
            self.after_cancel(self._session_timer_job)
        self._session_timer_job = self.after(1000, _tick)

    def _on_close(self) -> None:
        if self._session_timer_job:
            try:
                self.after_cancel(self._session_timer_job)
            except tk.TclError:
                pass
            self._session_timer_job = None
        try:
            self.review_db.end_session(self.session_id)
            self.review_db.close()
        finally:
            self.destroy()

    def _install_keyboard_shortcuts(self) -> None:
        def _refresh_target(event=None) -> None:
            tab = self._active_tab()
            if tab:
                tab.update_enter_target(self.focus_get())

        def _enter(event) -> str | None:
            tab = self._active_tab()
            if not tab:
                return None
            tab.update_enter_target(self.focus_get())
            invoked = tab.invoke_focused_or_default(self.focus_get())
            return "break" if invoked else None

        self.bind_all("<Return>", _enter, add="+")
        self.bind_all("<KP_Enter>", _enter, add="+")
        self.bind_all("<FocusIn>", _refresh_target, add="+")

    def _active_tab(self) -> KeyboardNavigableTab | None:
        if not self.notebook:
            return None
        selected = self.notebook.select()
        if not selected:
            return None
        try:
            widget = self.notebook.nametowidget(selected)
        except tk.TclError:
            return None
        if isinstance(widget, ScrollableTabHost):
            return widget.content
        if isinstance(widget, KeyboardNavigableTab):
            return widget
        return None

    def _on_tab_changed(self, event=None) -> None:
        tab = self._active_tab()
        if not tab:
            return
        if isinstance(tab, ReviewTab):
            tab.refresh_items(self._load_review_items())
        if isinstance(tab, ConjugationTab):
            tab.show_help()
        elif self.help_panel:
            self.help_panel.set_text(
                "Select a word or sentence to see pronunciation tips based on the guide."
            )
        tab.focus_default_button()
        tab.update_enter_target(self.focus_get())

    def _switch_language(self, key: str) -> None:
        if key == active_language_key():
            return
        set_active_module(key)
        self.language_var.set(key)
        self.registry = build_exercise_registry()
        self._apply_window_title()
        self._build_tabs()

    def _toggle_help_panel(self) -> None:
        if not self.help_panel:
            return
        if self.help_panel.winfo_ismapped():
            self.help_panel.grid_remove()
            self.guide_toggle_button.configure(text="Show guide")
        else:
            self.help_panel.grid()
            self.guide_toggle_button.configure(text="Hide guide")

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
