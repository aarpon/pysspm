from pathlib import Path

import typer

import pysspm.cli_config as command_config
import pysspm.cli_project as command_project
import pysspm.cli_stats as command_stats
from pysspm import __version__
from pysspm.config import ConfigurationParser

# Load configuration (singleton)
CONFIG_PARSER = ConfigurationParser()

# Instantiate Typer
app = typer.Typer(no_args_is_help=True)

# Add sub-commands
app.add_typer(command_config.app)
app.add_typer(command_project.app)
app.add_typer(command_stats.app)


@app.command("version")
def version():
    """Print version information."""
    typer.echo(f"Simple Scientific Project Manager v{__version__}")


def main():
    """Entry point for the sspm script."""
    app()


if __name__ == "__main__":
    main()
