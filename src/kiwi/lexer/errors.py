"""Definition of custom exceptions for lexer errors."""

from pydantic import BaseModel


class DebugInfo(BaseModel):
    """Debug information for lexer errors."""

    position: int
    line: int
    column: int
    text: str


class LexerError(Exception):
    """Base class for lexer-related errors."""

    def __init__(
        self,
        debug_info: DebugInfo,
        message: str,
    ) -> None:
        """Initialize LexerError."""
        self.debug_info: DebugInfo = debug_info
        self.message: str = message
        super().__init__(
            f"{self.__class__.__name__}: {message}. \nDebug info: {debug_info}"
        )


class InvalidTokenError(LexerError):
    """Exception raised for invalid tokens encountered during lexing."""

    def __init__(self, debug_info: DebugInfo) -> None:
        """
        Construct InvalidTokenError.

        Token: The invalid token encountered.
        Position: The position of the token in the source code.
        """
        self.debug_info: DebugInfo = debug_info
        super().__init__(debug_info, f"Invalid token! Debug info: {debug_info}")


class UnmatchedCategoryError(LexerError):
    """Exception raised when a token's category does not match the expected category."""

    def __init__(
        self,
        debug_info: DebugInfo,
        expected_category: str,
        actual_category: str,
    ) -> None:
        """Initialize UnmatchedCategory error."""
        super().__init__(
            debug_info,
            f"Expected category '{expected_category}', but got '{actual_category}'.",
        )
