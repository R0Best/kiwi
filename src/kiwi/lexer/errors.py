"""
Error hierarchy for the Kiwi Lexer.

This module provides a rich exception hierarchy that automatically formats
user-friendly, compiler-style error messages with visual pointers.
"""

from typing import Final, override

from kiwi.lexer.utils import DebugInfo


class LexerError(Exception):
    """
    Base class for all lexical analysis errors.

    This exception wraps `DebugInfo` to provide a standardized, visually
    distinct error report (including file path, line number, and a caret
    pointing to the specific column).
    """

    def __init__(self, message: str, debug_info: DebugInfo | None = None) -> None:
        """
        Initialize the error.

        Args:
            message: A descriptive error message.
            debug_info: Optional context about the error location.
        """
        self.message: Final[str] = message
        self.debug_info: Final[DebugInfo | None] = debug_info
        super().__init__(message)

    @override
    def __str__(self) -> str:
        """
        Render the error as a formatted compiler message.

        Returns:
            A string combining the message, file context, and a visual caret.
        """
        if not self.debug_info or not self.debug_info.source_line:
            return self.message

        info = self.debug_info

        # 0-based offset for the caret (column is 1-based)
        caret_offset = max(0, info.column - 1)
        caret_visual = " " * caret_offset + "^"

        # Format:
        # File "main.kiwi", line 10
        # var x = ?
        #         ^ Unexpected character
        return (
            f'\nFile "{info.filename}", line {info.line}\n'
            f"{info.source_line}\n"
            f"{caret_visual} {self.message}"
        )


class UnexpectedCharacterError(LexerError):
    """Raised when the Lexer encounters a character it cannot recognize."""

    def __init__(self, debug_info: DebugInfo) -> None:
        """
        Initialize the error.

        Args:
            debug_info: Optional context about the error location.
        """
        super().__init__("Unexpected character", debug_info)


class OutOfBoundsError(LexerError):
    """Raised if the Lexer attempts to read past the End Of File (EOF)."""
