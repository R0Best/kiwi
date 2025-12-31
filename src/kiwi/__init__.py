"""Initialize the kiwi package."""

from pathlib import Path

import typer

from kiwi.lexer import Lexer
from kiwi.lexer.tokens import TokenCategory

app = typer.Typer()


@app.command()
def lex(input_file: str) -> None:
    """Lex the source code from the given input file and print the tokens."""
    with Path(input_file).open("r") as file:
        lexer = Lexer(source_code=file.read())

    for token in lexer:
        typer.echo(token) if token.category != TokenCategory.WHITESPACE else None


@app.command()
def simulate(input_file: str) -> None:
    """Simulate the program found in the given input file."""


@app.command()
def compile_code(input_file: str, output_file: str) -> None:
    """Compile the source code from input_file and save to output_file."""


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
