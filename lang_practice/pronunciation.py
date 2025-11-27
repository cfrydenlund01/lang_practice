"""Delegates pronunciation helpers to the active language module."""

from __future__ import annotations

from .language_registry import get_module


def to_ipa(text: str, language: str | None = None) -> str:
    return get_module(language).to_ipa(text)


def to_phonetic(text: str, language: str | None = None) -> str:
    return get_module(language).to_phonetic(text)


def explain_pronunciation(text: str, language: str | None = None) -> str:
    return get_module(language).explain_pronunciation(text)
