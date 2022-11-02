import typer
from tabulate import tabulate

from ..lib.config import ConfigurationParser
from ..lib.project import ProjectManager
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

    # Retrieve the projects table
    project_dataframe = ProjectManager.get_projects(
        CONFIG_PARSER["projects.location"], detailed=True
    )

    if project_dataframe is None:
        typer.echo("No projects found.")
        return
    else:

        df_grouped = (
            project_dataframe.groupby(["Year", "Group"])
            .size()
            .reset_index(name="Projects")
        ).sort_values(by="Year", ascending=False)
        table = tabulate(
            df_grouped,
            headers=["Year", "Group", "Projects"],
            showindex=False,
            tablefmt="fancy_grid",
        )
        typer.echo(table)
