"""Registered language modules."""

from __future__ import annotations

from .french import MODULE as FRENCH_MODULE
from .italian import MODULE as ITALIAN_MODULE

MODULES = {
    FRENCH_MODULE.key: FRENCH_MODULE,
    ITALIAN_MODULE.key: ITALIAN_MODULE,
}

DEFAULT_LANGUAGE = FRENCH_MODULE.key

__all__ = ["MODULES", "DEFAULT_LANGUAGE"]
