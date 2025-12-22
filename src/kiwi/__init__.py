from pathlib import Path

import typer

from lexer.lexer import Lexer

app = typer.Typer()


@app.command()
def lex(input_file: str) -> None:
    for token in Lexer(source_code=Path(input_file).open().read()).tokenize():
        typer.echo(token)


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
