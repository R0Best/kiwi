# tests/unit/test_lexer.py
from kiwi.lexer.lexer import Lexer
from kiwi.lexer.tokens import TokenType


def test_lex_arithmetic():
    code = "10 + 20"
    tokens = Lexer(source_code=code).tokenize()

    # Filter noise for assertion
    real_tokens = [t for t in tokens if "WHITESPACE" not in t.type.name]

    assert len(real_tokens) == 3
    assert real_tokens[0].type == TokenType.LITERAL_NUMBER_INTEGER
    assert real_tokens[0].text == "10"
    assert real_tokens[1].type == TokenType.OPERATOR_ARITHMETIC_ADDITION
