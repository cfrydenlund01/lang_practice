"""gTTS-based text-to-speech client with simple caching."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional

from .language_registry import get_active_module

try:
    from gtts import gTTS
except ImportError:  # pragma: no cover - best effort fallback
    gTTS = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "cache" / "tts"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
HAS_GTTS = gTTS is not None


def _hash_text(text: str, lang: str) -> str:
    normalized = " ".join(text.strip().split()).lower()
    digest = hashlib.sha1(f"{lang}:{normalized}".encode("utf-8")).hexdigest()
    return digest


def _summarize_text(text: str, limit: int = 48) -> str:
    """Return a short snippet suitable for logging."""

    snippet = " ".join(text.strip().split())
    if len(snippet) <= limit:
        return snippet
    return f"{snippet[: limit - 3]}..."

def available() -> bool:
    return HAS_GTTS


def synthesize_to_file(text: str, lang: str | None = None) -> Optional[Path]:
    """Generate (or reuse cached) speech audio for ``text``."""

    if not text:
        return None
    if not HAS_GTTS:
        LOGGER.warning("gTTS not available; install the gtts package to enable audio.")
        return None

    lang_code = lang or get_active_module().tts_lang
    descriptor = _summarize_text(text)
    key = _hash_text(text, lang_code)
    path = CACHE_DIR / f"{key}.mp3"
    if path.exists():
        LOGGER.debug("Using cached speech for '%s'", descriptor)
        return path

    try:
        LOGGER.info("Requesting speech audio for '%s'", descriptor)
        tts = gTTS(text=text, lang=lang_code)
        tts.save(str(path))
        LOGGER.info("Received speech audio for '%s'", descriptor)
    except Exception as exc:  # pragma: no cover - network/runtime errors
        LOGGER.warning("Unable to synthesize speech: %s", exc)
        if path.exists():
            path.unlink(missing_ok=True)
        return None
    return path
