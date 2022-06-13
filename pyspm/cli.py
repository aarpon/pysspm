import typer

from . import __version__
from .conf import ConfigurationManager

# Load configuration
CONFIG_MANAGER = ConfigurationManager()

# Instantiate Typer
app = typer.Typer()


@app.command("config")
def config():
    """View and edit configuration options."""
    typer.echo("Allows to visualize and change configuration.")


@app.command("create")
def create_project(name: str, user_name: str, user_email: str, user_group: str):
    """Create new project."""
    typer.echo(f"Create a new project with the passed arguments.")


@app.command("stats")
def stats(filter=None):
    """Retrieve statistics."""
    typer.echo(f"Collect project statistics.")


@app.command("version")
def version():
    """Print version information."""
    typer.echo(
        f"spm -- Simple scientific project management tool version {__version__}."
    )


def main():
    """Entry point for the spm script."""
    typer.echo(f"spm entry point")
    typer.echo(f"Configuration file is valid: {CONFIG_MANAGER.is_valid}")
    app()


if __name__ == "__main__":
    typer.echo(CONFIG_MANAGER)
    app()
