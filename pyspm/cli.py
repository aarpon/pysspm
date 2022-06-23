import typer

import pyspm.cli_config as command_config
import pyspm.cli_project as command_project
import pyspm.cli_stats as command_stats
from pyspm import __version__
from pyspm.config import ConfigurationManager

# Load configuration (singleton)
CONFIG_MANAGER = ConfigurationManager()

# Instantiate Typer
app = typer.Typer(no_args_is_help=True)

# Add sub-commands
app.add_typer(command_config.app)
app.add_typer(command_project.app)
app.add_typer(command_stats.app)


@app.command("version")
def version():
    """Print version information."""
    typer.echo(f"Simple (scientific) Project Manager v{__version__}")


def main():
    """Entry point for the spm script."""
    app()


if __name__ == "__main__":
    typer.echo(CONFIG_MANAGER)
    app()
