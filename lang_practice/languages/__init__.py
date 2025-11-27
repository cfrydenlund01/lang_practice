"""Registered language modules."""

from __future__ import annotations

from .french import MODULE as FRENCH_MODULE

MODULES = {
    FRENCH_MODULE.key: FRENCH_MODULE,
}

DEFAULT_LANGUAGE = FRENCH_MODULE.key

__all__ = ["MODULES", "DEFAULT_LANGUAGE"]
