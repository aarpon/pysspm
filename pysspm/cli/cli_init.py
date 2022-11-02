from pathlib import Path

import typer

from ..lib.config import ConfigurationParser

__doc__ = "Command line actions to initialize sspm."

# Load configuration (singleton)
CONFIG_PARSER = ConfigurationParser()


def initialize():
    """Initialize sspm."""

    # If sspm is already initialized, inform and ask it it is okay to continue
    if CONFIG_PARSER.is_valid:
        current_project_location = CONFIG_PARSER["projects.location"]
        # Inform
        typer.echo(
            typer.style(
                f"sspm is already configured: `project_location = {current_project_location}`.",
                fg=typer.colors.GREEN,
                bold=True,
            )
        )
        re_init = input("Do you want to reinitialite sspm [y|N]?")
        if re_init is None or re_init == "":
            re_init = "N"
        if re_init.upper() != "Y":
            typer.echo("Leaving configuration untouched.")
            raise typer.Exit(0)

    # Inform
    typer.echo(
        typer.style(
            f"Initializing sspm:",
            fg=typer.colors.GREEN,
            bold=True,
        )
    )
    # Ask the user to provide a value for `projects.location`
    projects_location = input("Please specify `projects.location` = ")
    if projects_location == "":
        raise typer.Exit(1)
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
            raise typer.Exit(1)
        try:
            projects_location.mkdir(parents=True, exist_ok=True)
            print(f"Projects folder `{projects_location}` successfully created.")
        except OSError as e:
            typer.echo(
                typer.style(
                    f"Error: folder `{projects_location}` could not be created: {e}",
                    fg=typer.colors.RED,
                    bold=True,
                )
            )
            raise typer.Exit(1)
    typer.echo(f"Storing projects location in configuration file.")
    CONFIG_PARSER["projects.location"] = str(projects_location)
    typer.echo(
        typer.style(
            f"\nsspm initialized. Run `sspm config show` to visualize current configuration.",
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
