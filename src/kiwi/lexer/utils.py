"""Utility data structures for the Kiwi Lexer."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DebugInfo:
    """Immutable container for error context."""

    offending_text: str
    position: int
    line: int
    column: int
    filename: str = "<stdin>"
    source_line: str | None = None
    hint: str | None = None
