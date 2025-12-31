"""
Lexical analysis engine for the Kiwi programming language.

This module provides the definitive `Lexer` class, featuring Zero-Copy architecture,
LL(k) lookahead, backtracking support, and compiler-grade error reporting.
"""

import re
import sys
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import TracebackType
from typing import Final, Self

from kiwi.lexer.errors import LexerError, UnexpectedCharacterError
from kiwi.lexer.tokens import Token, TokenCategory, TokenType
from kiwi.lexer.utils import DebugInfo

# -----------------------------------------------------------------------------
# Configuration Constants
# -----------------------------------------------------------------------------

_INTERN_MAX_LENGTH: Final[int] = 20
_DEFAULT_FILENAME: Final[str] = "<stdin>"
_DEFAULT_ENCODING: Final[str] = "utf-8"
_START_LINE: Final[int] = 1
_START_COL: Final[int] = 1
_START_POS: Final[int] = 0

# -----------------------------------------------------------------------------
# Type Definitions
# -----------------------------------------------------------------------------

type TokenStream = Iterator[Token]


@dataclass(frozen=True, slots=True)
class LexerSnapshot:
    """Immutable capture of the Lexer's internal state for backtracking."""

    pos: int
    line: int
    col: int
    buffer: tuple[Token, ...]


@dataclass(frozen=True, slots=True)
class Location:
    """Value object representing a specific point in the source code."""

    pos: int
    line: int
    col: int


# -----------------------------------------------------------------------------
# Advanced Regex Compilation
# -----------------------------------------------------------------------------


def _is_literal_pattern(pattern: str) -> bool:
    """Check if pattern is a static keyword (no regex metacharacters)."""
    return not any(char in r".^$*+?{}[]\|()" for char in pattern)


@lru_cache(maxsize=1)
def _compile_master_regex() -> re.Pattern[str]:
    """
    Compiles a crash-safe master regex.

    Automatically sorts literal keywords by length (descending) to prevent
    prefix shadowing (e.g., ensuring 'iff' matches before 'if').
    """
    literals: list[TokenType] = []
    patterns: list[TokenType] = []

    for t in TokenType:
        if _is_literal_pattern(t.value):
            literals.append(t)
        else:
            patterns.append(t)

    literals.sort(key=lambda t: len(t.value), reverse=True)
    sorted_tokens = literals + patterns

    return re.compile("|".join(f"(?P<{t.name}>{t.value})" for t in sorted_tokens))


# -----------------------------------------------------------------------------
# The Lexer Engine
# -----------------------------------------------------------------------------


class Lexer:
    """
    A production-grade, buffered lexical analyzer.

    Features:
        - **O(N) Scanning**: Zero-copy processing via regex engine.
        - **LL(k) Lookahead**: Arbitrary `peek(offset)` support.
        - **Backtracking**: Snapshotting support.
        - **Visual Diagnostics**: Compiler-style error pointers.
    """

    __slots__ = (
        "_col",
        "_filename",
        "_ignore_types",
        "_line",
        "_master_regex",
        "_pos",
        "_source",
        "_strict_mode",
        "_token_buffer",
    )

    def __init__(
        self,
        source_code: str,
        filename: str = _DEFAULT_FILENAME,
        ignore_types: set[TokenType] | None = None,
        strict: bool = True,
    ) -> None:
        """
        Initialize the Lexer with source code and configuration.

        Args:
            source_code: The raw source text to analyze.
            filename: Label for error reporting contexts.
            ignore_types: TokenTypes to automatically skip (e.g., whitespace).
            strict: If True, raises errors immediately. If False, attempts
                to recover by skipping invalid characters.
        """
        self._source: Final[str] = source_code
        self._filename: Final[str] = filename
        self._strict_mode: Final[bool] = strict

        self._pos: int = _START_POS
        self._line: int = _START_LINE
        self._col: int = _START_COL

        self._master_regex: Final[re.Pattern[str]] = _compile_master_regex()
        self._ignore_types: Final[set[TokenType]] = ignore_types or set()
        self._token_buffer: deque[Token] = deque()

    @classmethod
    def from_file(cls, path: str | Path, encoding: str = _DEFAULT_ENCODING) -> Self:
        """Factory: Create a Lexer instance directly from a file path."""
        file_path = Path(path)
        return cls(file_path.read_text(encoding), str(file_path))

    # --- Public State Inspection ---

    @property
    def line(self) -> int:
        """Return the current 1-based line number."""
        return self._line

    @property
    def column(self) -> int:
        """Return the current 1-based column number."""
        return self._col

    @property
    def position(self) -> int:
        """Return the absolute 0-based character index."""
        return self._pos

    # --- Snapshotting (Backtracking) ---

    def create_snapshot(self) -> LexerSnapshot:
        """Capture the current state (cursor + buffer) for backtracking."""
        return LexerSnapshot(
            self._pos, self._line, self._col, tuple(self._token_buffer)
        )

    def restore_snapshot(self, snapshot: LexerSnapshot) -> None:
        """Restore the Lexer to a previously captured state."""
        self._pos = snapshot.pos
        self._line = snapshot.line
        self._col = snapshot.col
        self._token_buffer.clear()
        self._token_buffer.extend(snapshot.buffer)

    # --- Iteration & Lookahead ---

    def peek(self, offset: int = 0) -> Token | None:
        """
        Inspect upcoming tokens without consuming them.

        Args:
            offset: Number of steps ahead (0 = next token).

        Returns:
            The Token at the offset, or None if EOF is reached.
        """
        while len(self._token_buffer) <= offset:
            try:
                self._token_buffer.append(self._scan_next_valid_token())
            except StopIteration:
                return None
        return self._token_buffer[offset]

    def __enter__(self) -> Self:
        """Enable context manager support (e.g., `with Lexer(...) as l:`)."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Clean up resources (clear buffer) when exiting context."""
        self._token_buffer.clear()

    def __iter__(self) -> Self:
        """Return the lexer instance as an iterator."""
        return self

    def __next__(self) -> Token:
        """
        Retrieve the next token from the buffer or source stream.

        Returns:
            The next Token object.

        Raises:
            StopIteration: When source is exhausted.
            UnexpectedCharacterError: If strict mode is on and invalid input found.
        """
        if self._token_buffer:
            return self._token_buffer.popleft()
        return self._scan_next_valid_token()

    # --- Internal Engine (Hot Path) ---

    def _scan_next_valid_token(self) -> Token:
        while True:
            if self._is_eof():
                raise StopIteration

            match = self._master_regex.match(self._source, self._pos)

            if not match:
                self._handle_lexical_error()
                continue

            token = self._construct_token(match)

            if self._should_skip(token):
                continue

            return token

    def _is_eof(self) -> bool:
        return self._pos >= len(self._source)

    def _construct_token(self, match: re.Match[str]) -> Token:
        group_name = match.lastgroup
        if group_name is None:
            msg = "Internal Regex failure"
            raise self._create_error(msg)

        token_type = TokenType[group_name]
        text = match.group()
        start_loc = Location(self._pos, self._line, self._col)

        self._pos = match.end()
        self._update_location_fast(text)

        return Token(
            type=token_type,
            text=self._intern_if_eligible(text, token_type),
            position=start_loc.pos,
            line=start_loc.line,
            column=start_loc.col,
        )

    def _update_location_fast(self, text: str) -> None:
        if "\n" not in text:
            self._col += len(text)
            return

        self._line += text.count("\n")
        self._col = len(text) - text.rfind("\n")

    def _should_skip(self, token: Token) -> bool:
        return token.type in self._ignore_types

    def _handle_lexical_error(self) -> None:
        if self._strict_mode:
            raise self._create_visual_error()

        # Panic Recovery: Skip char and retry
        self._update_location_fast(self._source[self._pos])
        self._pos += 1

    def _intern_if_eligible(self, text: str, kind: TokenType) -> str:
        if kind.category == TokenCategory.IDENTIFIER and len(text) < _INTERN_MAX_LENGTH:
            return sys.intern(text)
        return text

    # --- Error Diagnostics ---

    def _create_visual_error(self) -> LexerError:
        """Generates a rich error object with captured context."""
        # 1. Capture the full line for context
        line_start = self._source.rfind("\n", 0, self._pos) + 1
        line_end = self._source.find("\n", self._pos)
        if line_end == -1:
            line_end = len(self._source)

        # 2. Extract raw data (No string formatting here!)
        source_line = self._source[line_start:line_end]

        # 3. Pass data to the Exception (It handles formatting)
        return UnexpectedCharacterError(
            DebugInfo(
                offending_text=self._source[self._pos],
                position=self._pos,
                line=self._line,
                column=self._col,
                filename=self._filename,
                source_line=source_line,
                hint="Check for illegal symbols or encoding issues.",
            )
        )

    def _create_error(self, msg: str) -> LexerError:
        return LexerError(msg)
