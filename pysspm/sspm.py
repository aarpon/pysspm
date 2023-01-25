import typer

from pysspm import __version__
from pysspm.cli.cli_config import app as command_config_app
from pysspm.cli.cli_init import initialize
from pysspm.cli.cli_project import app as command_project_app
from pysspm.cli.cli_stats import app as command_stats_app
from pysspm.lib.config import ConfigurationParser

# Load configuration (singleton)
CONFIG_PARSER = ConfigurationParser()

# Instantiate Typer
app = typer.Typer(no_args_is_help=True)

# Add sub-commands
app.add_typer(command_config_app)
app.add_typer(command_project_app)
app.add_typer(command_stats_app)


@app.command("version")
def version():
    """Print version information."""
    typer.echo(f"Simple Scientific Project Manager v{__version__}")


@app.command("init")
def init():
    """Initialize."""
    initialize()


def main():
    """Entry point for the sspm script."""
    app()


if __name__ == "__main__":
    main()
