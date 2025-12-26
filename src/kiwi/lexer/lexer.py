"""Package responsible for tokenizing source code into tokens."""

import re

from pydantic import BaseModel

from kiwi.lexer.tokens import Token, TokenCategory, TokenType


class Lexer(BaseModel):
    """The Lexer class is responsible for tokenizing the source code."""

    source_code: str
    position: int = 0
    line: int = 1
    column: int = 1

    def advance(self, steps: int) -> None:
        """Increase the position by 1."""
        for _ in range(steps):
            if self.position < len(self.source_code):
                self.position += 1

                if self.is_token_type(self.peek(), TokenType.WHITESPACE_LINE_FEED):
                    self.line += 1
                    self.column = 0
                else:
                    self.column += 1

    def peek(self, char_count: int = 1) -> str:
        """Peek ahead by offset characters."""
        return self.source_code[self.position : self.position + char_count]

    @property
    def next_token(self) -> Token:
        """
        Get the next token from the source code.

        This will not advance the position of the lexer.
        """
        for token_type in TokenType:
            regex: str = token_type.value
            match = re.match(regex, self.peek(len(self.source_code) - self.position))

            if match:
                return Token(
                    type=token_type,
                    text=match.group(0),
                    position=self.position,
                    line=self.line,
                    column=self.column,
                )

        raise NotImplementedError

    @staticmethod
    def is_token_type(word: str, token_type: TokenType) -> bool:
        """Check if the word matches the regex provided by the token_type."""
        return re.compile(token_type).fullmatch(word) is not None

    @staticmethod
    def is_token_category(word: str, token_category: TokenCategory) -> bool:
        """Check if the word matches with any regex associated with TokenCategory."""
        return any(
            Lexer.is_token_type(word, token_type)
            if token_type.category == token_category
            else False
            for token_type in TokenType
        )

    def tokenize(self) -> list[Token]:
        """Generate all the tokens from the source code."""
        tokens: list[Token] = []
        while self.position < len(self.source_code):
            token: Token = self.next_token
            if token is None:
                break
            tokens.append(token)
            self.advance(len(token.text))
        return tokens
