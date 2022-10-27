from pathlib import Path

import typer

from pysspm.config import ConfigurationParser

# Load configuration (singleton)
CONFIG_PARSER = ConfigurationParser()


def initialize():
    """Initialize sspm."""

    # Inform
    typer.echo(
        typer.style(
            f"Initializing sspm:",
            fg=typer.colors.GREEN,
            bold=True,
        )
    )
    typer.echo(f"Initialized configuration file `{CONFIG_PARSER.config_file}`.")

    # Ask the user to provide a value for `projects.location`
    projects_location = input("Please specify `projects.location` = ")
    if projects_location == "":
        raise typer.Exit()
    projects_location = Path(projects_location)
    if projects_location.is_dir():
        typer.echo(f"Folder {projects_location} already exists.")
    else:
        create_projects_location = input(
            f"Projects folder `{projects_location}` does not exist. Create [Y|n]? "
        )
        if create_projects_location is None or create_projects_location == "":
            create_projects_location = "Y"
        if create_projects_location.upper() != "Y":
            raise typer.Exit()
        try:
            projects_location.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            typer.echo(
                typer.style(
                    f"Sorry, folder `{projects_location}` could not be created: {e}",
                    fg=typer.colors.RED,
                    bold=True,
                )
            )
            raise typer.Exit()
    typer.echo(f"Updating configuration.")
    CONFIG_PARSER["projects.location"] = str(projects_location)
    typer.echo(
        typer.style(
            f"sspm initialized. Run `sspm config show` to visualize current configuration.",
            fg=typer.colors.GREEN,
            bold=True,
        )
    )


def check_if_initialized():
    """Check if sspm has been configured yet. If not, start an interactive initalization."""

    if not CONFIG_PARSER.is_valid:
        typer.echo(
            typer.style(
                "sspm has not been configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        initialize()
