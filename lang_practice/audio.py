"""Helpers for lightweight audio playback."""

from __future__ import annotations

import logging
from pathlib import Path

try:
    from playsound import playsound
except ImportError:  # pragma: no cover - optional dependency
    playsound = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)


def play_audio(path: Path) -> bool:
    """Play an audio file using the playsound package."""

    if not path or not path.exists():
        LOGGER.warning("Audio file not found: %s", path)
        return False
    if playsound is None:
        LOGGER.warning("playsound package is not installed; cannot play audio.")
        return False
    try:
        playsound(str(path), block=False)
        return True
    except Exception as exc:  # pragma: no cover - playback errors vary per platform
        LOGGER.warning("Unable to play audio: %s", exc)
        return False
