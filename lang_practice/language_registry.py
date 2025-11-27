"""Manage available language modules and persist the active selection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .languages import DEFAULT_LANGUAGE, MODULES
from .languages.base import LanguageModule

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = PROJECT_ROOT / "cache" / "settings.json"

_active_key: str | None = None


def _load_last_key() -> str | None:
    if not STATE_PATH.exists():
        return None
    try:
        payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload.get("last_language")


def _save_last_key(key: str) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"last_language": key}
    STATE_PATH.write_text(json.dumps(payload), encoding="utf-8")


def available_modules() -> Dict[str, LanguageModule]:
    """Return the registered language modules keyed by identifier."""

    return MODULES


def active_language_key() -> str:
    """Return the currently active language key, loading persisted choice if present."""

    global _active_key
    if _active_key is None:
        _active_key = _load_last_key() or DEFAULT_LANGUAGE
    if _active_key not in MODULES:
        _active_key = DEFAULT_LANGUAGE
    return _active_key


def get_active_module() -> LanguageModule:
    """Return the currently active language module."""

    return MODULES[active_language_key()]


def get_module(key: str | None = None) -> LanguageModule:
    """Return the requested language module or the active module by default."""

    if key is None:
        return get_active_module()
    if key not in MODULES:
        raise KeyError(f"Unknown language module: {key}")
    return MODULES[key]


def set_active_module(key: str) -> LanguageModule:
    """Switch to a new language module and persist the selection."""

    if key not in MODULES:
        raise KeyError(f"Unknown language module: {key}")
    global _active_key
    _active_key = key
    _save_last_key(key)
    return MODULES[key]
