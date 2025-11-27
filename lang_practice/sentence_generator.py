"""Delegate sentence generation to the active language module."""

from __future__ import annotations

from .language_registry import get_module
from .models import Sentence


def generate_sentence(category: str | None = None, language: str | None = None) -> Sentence:
    module = get_module(language)
    return module.generate_sentence(category)
