"""
Token Definitions and Data Models for the Kiwi Lexer.

This module serves as the "grammar definition" for the lexical analysis phase.
It defines:
1.  **TokenCategory**: High-level groupings (e.g., all operators, all keywords).
2.  **TokenType**: Specific lexical units with their corresponding Regex patterns.
3.  **Token**: The immutable data carrier for a matched lexeme.

Architecture Note:
    This module uses a "Convention over Configuration" pattern. The name of a
    `TokenType` member (e.g., `KEYWORD_IF`) determines its `TokenCategory`
    (e.g., `KEYWORD`). This is handled automatically by the `_get_category_map`
    function, ensuring O(1) lookups without manual mapping tables.
"""

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache

# -----------------------------------------------------------------------------
# 1. Token Categories
# -----------------------------------------------------------------------------


class TokenCategory(StrEnum):
    """
    High-level classification of tokens.

    These categories are primarily used by the Parser to skip broad classes
    of tokens (like Whitespace or Comments) or to make high-level decisions
    (e.g., "expecting a Literal").
    """

    KEYWORD = "KEYWORD"
    """Reserved words that define control flow or structure (e.g., if, while)."""

    SEPARATOR = "SEPARATOR"
    """Punctuation used to delimit structure (e.g., ;, {, }, ,)."""

    OPERATOR = "OPERATOR"
    """Symbols that perform operations on operands (e.g., +, ==, =)."""

    LITERAL = "LITERAL"
    """Static values defined directly in the source (e.g., 123, "hello")."""

    COMMENT = "COMMENT"
    """Code annotations ignored by the compiler."""

    WHITESPACE = "WHITESPACE"
    """Spacing characters (spaces, tabs, newlines)."""

    IDENTIFIER = "IDENTIFIER"
    """Names given to variables, functions, macros, or types."""

    UNKNOWN = "UNKNOWN"
    """Fallback for characters that do not match any defined rule."""

    @classmethod
    def from_token_type(cls, token_type: "TokenType") -> "TokenCategory":
        """
        Derives the category from a specific TokenType.

        Args:
            token_type: The specific TokenType to classify.

        Returns:
            The corresponding TokenCategory.
        """
        # Uses the cached lookup map for O(1) performance
        return _get_category_map()[token_type]


# -----------------------------------------------------------------------------
# 2. Token Types (The Grammar)
# -----------------------------------------------------------------------------


class TokenType(StrEnum):
    """Enumeration of all valid token types in the Kiwi language.

    **Lexing Rules:**
    1. **Precedence**: The Lexer (engine.py) sorts 'Literal' patterns (keywords)
       by length to prevent shadowing (e.g., matching 'iff' before 'if').
    2. **Complex Patterns**: Regex-based patterns (identifiers, numbers) are
       matched in the order defined below.
    """

    # =========================================================================
    # SECTION: COMMENTS  # noqa: ERA001
    # =========================================================================
    # Matches: |- multi-line comments -|
    # Logic: Match start marker, then any char or newline non-greedily, then end marker.
    COMMENT_MULTI_LINE = r"\|-(.|\n)*?-\|"

    # Matches: | single-line comments
    COMMENT_SINGLE_LINE = r"\|.*"

    # =========================================================================
    # SECTION: KEYWORDS  # noqa: ERA001
    # =========================================================================

    # --- Control Flow ---
    KEYWORD_IF = r"\bif\b"
    KEYWORD_ELIF = r"\belif\b"
    KEYWORD_ELSE = r"\belse\b"
    KEYWORD_BREAK = r"\bbreak\b"
    KEYWORD_CONTINUE = r"\bcontinue\b"
    KEYWORD_RETURN = r"\breturn\b"

    # --- Iteration ---
    KEYWORD_LOOP = r"\bloop\b"
    KEYWORD_FOR = r"\bfor\b"
    KEYWORD_WHILE = r"\bwhile\b"
    KEYWORD_DO = r"\bdo\b"

    # --- Modules & Imports ---
    KEYWORD_USE = r"\buse\b"
    KEYWORD_AS = r"\bas\b"

    # --- Concurrency ---
    KEYWORD_ASYNC = r"\basync\b"
    KEYWORD_AWAIT = r"\bawait\b"

    # --- Object Oriented Programming ---
    KEYWORD_SELF = r"\bSelf\b"

    # --- Miscellaneous ---
    # Matches 'in' only when it is a whole word (not inside 'integer')
    KEYWORD_IN = r"\bin\b"

    # =========================================================================
    # SECTION: OPERATORS  # noqa: ERA001
    # =========================================================================

    # --- Binary (Bitwise) Operators ---
    # Note: These use 'b' prefixes to distinguish from logical ops
    OPERATOR_BINARY_NIMPLY = r"bNIMPLY"
    OPERATOR_BINARY_IMPLY = r"bIMPLY"
    OPERATOR_BINARY_XNOR = r"bXNOR"
    OPERATOR_BINARY_NAND = r"bNAND"
    OPERATOR_BINARY_XOR = r"bXOR"
    OPERATOR_BINARY_NOR = r"bNOR"
    OPERATOR_BINARY_NOT = r"bNOT"
    OPERATOR_BINARY_AND = r"bAND"
    OPERATOR_BINARY_OR = r"bOR"

    # --- Logical (Boolean) Operators ---
    OPERATOR_LOGICAL_NIMPLY = r"NIMPLY"
    OPERATOR_LOGICAL_IMPLY = r"IMPLY"
    OPERATOR_LOGICAL_XNOR = r"XNOR"
    OPERATOR_LOGICAL_NAND = r"NAND"
    OPERATOR_LOGICAL_XOR = r"XOR"
    OPERATOR_LOGICAL_NOR = r"NOR"
    OPERATOR_LOGICAL_NOT = r"NOT"
    OPERATOR_LOGICAL_AND = r"AND"
    OPERATOR_LOGICAL_OR = r"OR"

    # --- Structural Operators ---
    SEPARATOR_ARROW = r"->"

    # --- Relational (Comparison) Operators ---
    OPERATOR_RELATIONAL_LOWER_EQUAL = r"<="
    OPERATOR_RELATIONAL_GREATER_EQUAL = r">="
    OPERATOR_RELATIONAL_EQUAL = r"=="
    OPERATOR_RELATIONAL_NOT_EQUAL = r"!="
    # Less/Greater must come *after* <= and >= to prevent partial matching
    OPERATOR_RELATIONAL_LOWER = r"<"
    OPERATOR_RELATIONAL_GREATER = r">"

    # --- Assignment (Compound) Operators ---
    OPERATOR_ASSIGNMENT_ADDITION = r"\+="
    OPERATOR_ASSIGNMENT_SUBTRACTION = r"-="
    OPERATOR_ASSIGNMENT_MULTIPLICATION = r"\*="
    OPERATOR_ASSIGNMENT_DIVISION = r"/="
    OPERATOR_ASSIGNMENT_MODULO = r"%="
    OPERATOR_ASSIGNMENT_EXPONENTIATION = r"\^="
    OPERATOR_ASSIGNMENT = r"="

    # --- Arithmetic Operators ---
    OPERATOR_ARITHMETIC_ADDITION = r"\+"
    OPERATOR_ARITHMETIC_SUBTRACTION = r"-"
    OPERATOR_ARITHMETIC_MULTIPLICATION = r"\*"
    OPERATOR_ARITHMETIC_DIVISION = r"/"
    OPERATOR_ARITHMETIC_MODULO = r"%"
    OPERATOR_ARITHMETIC_EXPONENTIATION = r"\^"

    # =========================================================================
    # SECTION: LITERALS  # noqa: ERA001
    # =========================================================================

    # --- String Literals ---
    # Raw String: r"..." (No escape sequence processing)
    LITERAL_STRING_RAW = r'r"([^"])*"'

    # Byte String: b"..."
    LITERAL_STRING_BYTE = r'b"([^"\\]|\\.)*"'

    # Standard String: "..." (Supports escaped quotes like \")
    LITERAL_STRING = r'"([^"\\]|\\.)*"'

    # Character: 'c'  # noqa: ERA001
    LITERAL_CHAR = r"'([^'\\]|\\.)'"

    # --- Numeric Literals ---
    # Hexadecimal: 0x1A...
    LITERAL_NUMBER_HEX = r"0[xX][0-9a-fA-F]+"

    # Binary: 0b101...
    LITERAL_NUMBER_BINARY = r"0[bB][01]+"

    # Float: 1.0, .5, 1e10. Matches decimals or scientific notation.
    LITERAL_NUMBER_FLOAT = r"(\d+\.\d*|\.\d+)([eE][+-]?\d+)?|\d+[eE][+-]?\d+"

    # Integer: 123, 1_000 (Supports underscores)
    LITERAL_NUMBER_INTEGER = r"\d(?:_?\d)*"

    # =========================================================================
    # SECTION: SEPARATORS & PUNCTUATION  # noqa: ERA001
    # =========================================================================

    SEPARATOR_ELLIPSIS = r"\.\.\."
    SEPARATOR_DOUBLE_COLON = r"::"
    SEPARATOR_BRACKET_ROUND_OPEN = r"\("
    SEPARATOR_BRACKET_ROUND_CLOSED = r"\)"
    SEPARATOR_BRACKET_SQUARE_OPEN = r"\["
    SEPARATOR_BRACKET_SQUARE_CLOSED = r"\]"
    SEPARATOR_BRACKET_CURLY_OPEN = r"\{"
    SEPARATOR_BRACKET_CURLY_CLOSED = r"\}"
    SEPARATOR_COMMA = r","
    SEPARATOR_PERIOD = r"\."
    SEPARATOR_EXCLAMATION_POINT = r"!"
    SEPARATOR_QUESTION_MARK = r"\?"
    SEPARATOR_COLON = r":"
    SEPARATOR_SEMICOLON = r";"

    # =========================================================================
    # SECTION: WHITESPACE  # noqa: ERA001
    # =========================================================================

    WHITESPACE_SPACE = r" "
    WHITESPACE_CHARACTER_TAB = r"\t"
    WHITESPACE_VERTICAL_TAB = r"\v"
    WHITESPACE_FORM_FEED = r"\f"
    WHITESPACE_CARRIAGE_RETURN = r"\r"
    WHITESPACE_LINE_FEED = r"\n"
    WHITESPACE_EOF = r"$"

    # =========================================================================
    # SECTION: IDENTIFIERS  # noqa: ERA001
    # =========================================================================

    # Macro: Ends with '!' (e.g., println!)
    IDENTIFIER_MACRO = r"[a-zA-Z_][a-zA-Z0-9_]*!"

    # Decorator: Starts with '@' (e.g., @static)
    IDENTIFIER_DECORATOR = r"@[a-zA-Z_][a-zA-Z0-9_]*"

    # Standard Identifier: Variables, Function names
    IDENTIFIER_IDENTIFIER = r"[a-zA-Z_][a-zA-Z0-9_]*"

    @property
    def category(self) -> TokenCategory:
        """Helper to get the category associated with this type."""
        return TokenCategory.from_token_type(self)


# -----------------------------------------------------------------------------
# 3. Internal Mapping Logic
# -----------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _get_category_map() -> dict[TokenType, TokenCategory]:
    """
    Builds a high-performance O(1) lookup table for Token categories.

    Logic:
        Iterates over all TokenTypes and matches their name prefix against
        TokenCategory names.
        Example: TokenType.KEYWORD_IF -> TokenCategory.KEYWORD
    """
    mapping = {}
    for token_type in TokenType:
        found = False
        for category in TokenCategory:
            # We match the prefix of the enum member name (e.g., 'OPERATOR_...')
            if token_type.name.startswith(category.name):
                mapping[token_type] = category
                found = True
                break

        if not found:
            # Fallback for tokens that don't match standard naming conventions
            mapping[token_type] = TokenCategory.UNKNOWN

    return mapping


# -----------------------------------------------------------------------------
# 4. Token Data Model
# -----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Token:
    """
    Immutable representation of a lexical unit (Token).

    This object is created by the Lexer and consumed by the Parser.
    Using `slots=True` ensures minimal memory footprint, which is critical
    when compiling large source files containing millions of tokens.

    Attributes:
        type: The specific classification of the token (e.g., KEYWORD_IF).
        text: The actual text content matched from the source code.
        position: The 0-based absolute character index in the source.
        line: The 1-based line number.
        column: The 1-based column number.
    """

    type: TokenType
    text: str
    position: int
    line: int
    column: int

    @property
    def category(self) -> TokenCategory:
        """Convenience accessor for the token's high-level category.

        Useful for broad parsing logic (e.g., "skip all WHITESPACE").
        """
        return self.type.category
