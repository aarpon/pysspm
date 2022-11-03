import typer
from tabulate import tabulate

from ..lib.config import ConfigurationParser
from ..lib.stats import StatisticManager
from .cli_init import check_if_initialized

__doc__ = "Command line actions to collect project statistics."


# Load configuration (singleton)
CONFIG_PARSER = ConfigurationParser()

# Instantiate Typer
app = typer.Typer(name="stats", help="Collect statistics.")


@app.command("show")
def show():
    """Show count of projects by year and group."""

    # Make sure sspm configuration is initialized
    check_if_initialized()

    # Retrieve the statistics data frame
    try:
        statistics_dataframe = StatisticManager.get_stats(
            CONFIG_PARSER["projects.location"],
        )
    except Exception as e:
        typer.echo(
            typer.style(
                f"Error: could not retrieve statistics. {e}",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit(1)

    if statistics_dataframe is None:
        typer.echo("No projects found.")
        typer.Exit(0)

    # Display statistics table
    table = tabulate(
        statistics_dataframe,
        headers=["Year", "Group", "Projects"],
        showindex=False,
        tablefmt="fancy_grid",
    )
    typer.echo(table)
