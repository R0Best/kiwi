# tests/unit/test_lexer.py
from kiwi.lexer.lexer import Lexer
from kiwi.lexer.tokens import TokenType


def test_lex_arithmetic():
    code = "10 + 20"
    tokens = list(Lexer(source_code=code))

    assert len(tokens) == 3
    assert tokens[0].type == TokenType.LITERAL_NUMBER_INTEGER
    assert tokens[0].text == "10"
    assert tokens[1].type == TokenType.OPERATOR_ARITHMETIC_ADDITION
