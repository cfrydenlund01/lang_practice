# lang_practice

Modular Python application that provides a GUI for practicing vocabulary,
sentences, pronunciation, and verb conjugations. Modules live under
`lang_practice/languages/` (the current build ships with French and Italian modules) and
you can switch between them from the Language menu; the app remembers the last
language you used.

## Features

* Flashcard translation drills with IPA/phonetic helpers, TTS playback, and Previous/Next navigation.
* Flip-card memorization tab for quick front/back review of vocab and sentences.
* Sentence practice tab mixing curated lines with generated sentences.
* Present tense verb conjugation drills with pronunciation guidance.
* Accent toolbar to quickly insert language-specific characters while typing answers.
* Language selector in the menu bar with persisted last-used module.

## Getting started

Install Python dependencies (standard library + optional audio helpers) and launch the GUI:

```bash
# From the repo root (this folder), run the package as a module:
python -m lang_practice

# Note (Windows/PowerShell): these path-based invocations will fail:
#   python -m .\lang_practice\
#   python .\lang_practice\
```

Use the tab bar to switch between flashcards, sentence practice, flip cards,
and conjugation drills. Each screen shows the target-language text, IPA
transcription, and a learner-friendly phonetic line. If online TTS is
configured you can press the "Listen" button to hear the sentence or word.

## Text-to-speech (gTTS) support

Audio playback uses [gTTS](https://pypi.org/project/gTTS/) (Google Translate TTS) and
[`playsound`](https://pypi.org/project/playsound/). Install them to enable the “Listen”
buttons:

```bash
pip install gtts playsound==1.2.2
```

Notes:

- gTTS requires an active internet connection.
- Audio files are cached in `cache/tts/` so repeated sentences reuse the same MP3.
- If playback fails, ensure speakers are available and `playsound` is correctly installed.
- The Listen buttons now show a small progress indicator under them so you can confirm when audio is being requested/received.
- The TTS client logs when audio is requested or reused from cache; run with logging enabled to see those signals.
- Set `LANG_PRACTICE_TTS_ENABLED=0` (or the legacy `FRENCH_TTS_ENABLED=0`) in the environment to disable TTS and hide the buttons.
- The most recent `playsound` release (1.3.0) can fail to build on Windows/Python 3.12; version `1.2.2` is known to work reliably.

## Vocabulary data

Core vocabulary lives inside each module's `data.py` file:

- French: `lang_practice/languages/french/data.py`
- Italian: `lang_practice/languages/italian/data.py`

Update the language module files or sentence generator when adding new vocab or categories.
