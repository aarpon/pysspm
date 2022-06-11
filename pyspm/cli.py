import sys

import typer

from . import __version__

# Instantiate Typer
app = typer.Typer()


@app.command()
def version():
    """Print version information."""
    print(f"spm -- Simple scientific project management tool version {__version__}.")


@app.command()
def config():
    """View and edit configuration options."""
    print("Allows to visualize and change configuration.")


# Entry point for the spm script
def cli():
    app()
