from pathlib import Path

import typer
from lexer.lexer import Lexer
from lexer.tokens import TokenCategory, TokenType

app = typer.Typer()


@app.command()
def lex(input_file: str) -> None:
    with Path(input_file).open("r") as file:
        lexer = Lexer(source_code=file.read())

    for token in lexer.tokenize():
        typer.echo(token) if token.category != TokenCategory.WHITESPACE else None


@app.command()
def simulate(input_file: str) -> None:
    """Simulate the program found in the given input file."""


@app.command()
def compile(input_file: str, output_file: str) -> None:
    """Compile the source code from input_file and save to output_file."""


def main():
    app()


if __name__ == "__main__":
    main()
