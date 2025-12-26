"""Definitions of the token types and the token models for the lexer."""

from enum import StrEnum

from lexer.errors import DebugInfo, UnmatchedCategoryError
from pydantic import BaseModel, Field, model_validator


class TokenCategory(StrEnum):
    """Enumeration of all token categories."""

    KEYWORD = "KEYWORD"
    SEPARATOR = "SEPARATOR"
    OPERATOR = "OPERATOR"
    LITERAL = "LITERAL"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    IDENTIFIER = "IDENTIFIER"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def from_token_type(token_type: "TokenType") -> "TokenCategory":
        """Convert TokenType to TokenCategory."""
        for token_category in TokenCategory:
            if token_type.name.startswith(token_category):
                return token_category

        raise NotImplementedError


class TokenType(StrEnum):
    """
    Enumeration of all token types. The value of each member is the regex pattern.

    IMPORTANT: Order matters for regex matching, more specific patterns must come first.
    """

    # --- COMMENTS ---
    COMMENT_MULTI_LINE = r"---(.|\n)*?---"
    COMMENT_SINGLE_LINE = r"--.*"

    # --- KEYWORDS ---

    #   --- Control Flow ---
    KEYWORD_ELIF = r"elif"
    KEYWORD_ELSE = r"else"
    KEYWORD_IF = r"if"
    KEYWORD_RETURN = r"return"

    #   --- Packaging ---
    KEYWORD_USE = r"use"

    # --- OPERATORS ---

    #   --- Binary operators ---
    OPERATOR_BINARY_NIMPLY = r"bNIMPLY"
    OPERATOR_BINARY_IMPLY = r"bIMPLY"
    OPERATOR_BINARY_XNOR = r"bXNOR"
    OPERATOR_BINARY_NAND = r"bNAND"
    OPERATOR_BINARY_XOR = r"bXOR"
    OPERATOR_BINARY_NOR = r"bNOR"
    OPERATOR_BINARY_NOT = r"bNOT"
    OPERATOR_BINARY_AND = r"bAND"
    OPERATOR_BINARY_OR = r"bOR"

    #   --- Logical operators ---
    OPERATOR_LOGICAL_NIMPLY = r"NIMPLY"
    OPERATOR_LOGICAL_IMPLY = r"IMPLY"
    OPERATOR_LOGICAL_XNOR = r"XNOR"
    OPERATOR_LOGICAL_NAND = r"NAND"
    OPERATOR_LOGICAL_XOR = r"XOR"
    OPERATOR_LOGICAL_NOR = r"NOR"
    OPERATOR_LOGICAL_NOT = r"NOT"
    OPERATOR_LOGICAL_AND = r"AND"
    OPERATOR_LOGICAL_OR = r"OR"

    SEPARATOR_ARROW = r"->"

    #   --- Relational operators ---
    OPERATOR_RELATIONAL_LOWER_EQUAL = r"<="
    OPERATOR_RELATIONAL_GREATER_EQUAL = r">="
    OPERATOR_RELATIONAL_EQUAL = r"=="
    OPERATOR_RELATIONAL_NOT_EQUAL = r"!="
    OPERATOR_RELATIONAL_LOWER = r"<"
    OPERATOR_RELATIONAL_GREATER = r">"

    #   --- Assignment operators ---
    OPERATOR_ASSIGNMENT_ADDITION = r"\+="
    OPERATOR_ASSIGNMENT_SUBTRACTION = r"-="
    OPERATOR_ASSIGNMENT_MULTIPLICATION = r"\*="
    OPERATOR_ASSIGNMENT_DIVISION = r"/="
    OPERATOR_ASSIGNMENT_MODULO = r"%="
    OPERATOR_ASSIGNMENT_EXPONENTIATION = r"\^="
    OPERATOR_ASSIGNMENT = r"="

    #   --- Arithmetic operators ---
    OPERATOR_ARITHMETIC_ADDITION = r"\+"
    OPERATOR_ARITHMETIC_SUBTRACTION = r"-"
    OPERATOR_ARITHMETIC_MULTIPLICATION = r"\*"
    OPERATOR_ARITHMETIC_DIVISION = r"/"
    OPERATOR_ARITHMETIC_MODULO = r"%"
    OPERATOR_ARITHMETIC_EXPONENTIATION = r"\^"

    # --- LITERALS ---
    LITERAL_STRING = r'"([^"\\]|\\.)*"'
    LITERAL_CHARACTER = r"'([^'\\]|\\.)'"
    LITERAL_NUMBER_HEX = r"0[xX][0-9a-fA-F]+"
    LITERAL_NUMBER_BINARY = r"0[bB][01]+"
    LITERAL_NUMBER_FLOAT = r"\d+\.\d+"
    LITERAL_NUMBER_INTEGER = r"\d+"

    # --- SEPARATORS ---
    SEPARATOR_ELLIPSIS = r"\.\.\."
    SEPARATOR_BRACKET_ROUND_OPEN = r"\("
    SEPARATOR_BRACKET_ROUND_CLOSED = r"\)"
    SEPARATOR_BRACKET_SQUARE_OPEN = r"\["
    SEPARATOR_BRACKET_SQUARE_CLOSED = r"\]"
    SEPARATOR_BRACKET_CURLY_OPEN = r"\{"
    SEPARATOR_BRACKET_CURLY_CLOSED = r"\}"
    SEPARATOR_QUOTE_DOUBLE = r'"'
    SEPARATOR_QUOTE_SINGLE = r"'"
    SEPARATOR_COMMA = r","
    SEPARATOR_PERIOD = r"\."
    SEPARATOR_EXCLAMATION_POINT = r"!"
    SEPARATOR_QUESTION_MARK = r"\?"
    SEPARATOR_COLON = r":"
    SEPARATOR_SEMICOLON = r";"

    # --- WHITESPACE ---
    WHITESPACE_SPACE = r" "
    WHITESPACE_CHARACTER_TAB = r"\t"
    WHITESPACE_VERTICAL_TAB = r"\v"
    WHITESPACE_FORM_FEED = r"\f"
    WHITESPACE_CARRIAGE_RETURN = r"\r"
    WHITESPACE_LINE_FEED = r"\n"
    WHITESPACE_EOF = r"$"

    # --- IDENTIFIER ---
    IDENTIFIER_MACRO = r"[a-zA-Z_][a-zA-Z0-9_]*!"
    IDENTIFIER_DECORATOR = r"@[a-zA-Z_][a-zA-Z0-9_]*"
    IDENTIFIER_IDENTIFIER = r"[a-zA-Z_][a-zA-Z0-9_]*"

    # --- UNKNOWN ---
    UNKNOWN_CHARACTER = r"."
    UNKNOWN_WORD = r".+"

    @property
    def category(self) -> TokenCategory:
        """Convert TokenType to TokenCategory."""
        return TokenCategory.from_token_type(self)


class Token(BaseModel):
    """The token model."""

    type: TokenType = Field(...)
    text: str = Field(...)
    position: int = Field(...)
    line: int = Field(...)
    column: int = Field(...)

    @property
    def category(self) -> TokenCategory:
        """Get the category of the token."""
        return self.type.category

    @model_validator(mode="after")
    def post_init_check(self) -> "Token":
        """Run additional checks after initialization."""
        if self.type.category != self.category:
            raise UnmatchedCategoryError(
                debug_info=DebugInfo(
                    position=self.position,
                    line=self.line,
                    column=self.column,
                    text=self.text,
                ),
                expected_category=self.type.category,
                actual_category=self.category,
            )

        return self
