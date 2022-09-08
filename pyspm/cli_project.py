import os
import re
import subprocess
from pathlib import Path

import typer
from tabulate import tabulate

from pyspm.config import ConfigurationManager, MetadataManager
from pyspm.project import Project, ProjectManager

# Load configuration (singleton)
CONFIG_MANAGER = ConfigurationManager()

# Instantiate Typer
app = typer.Typer(name="project", help="Manage projects.")


@app.command("create")
def create(
    title: str = None,
    user_name: str = None,
    user_email: str = None,
    user_group: str = None,
    short_descr: str = None,
    extern_git_repos: str = None,
):
    """Create a new project."""

    # Check that we have a valid configuration
    if not CONFIG_MANAGER.is_valid:
        typer.echo(
            typer.style(
                "Error: spm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        raise typer.Exit()

    #
    # Parse the inputs
    #

    if title is None or len(user_name) == 0:
        title = input("[*] Project title: ")

    while user_name is None or len(user_name) == 0:
        user_name = input("[*] User's first and family name: ")

    while user_email is None or not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", user_email):
        user_email = input("[*] User's e-mail address: ")

    while user_group is None or len(user_group) == 0:
        user_group = input("[*] User's (scientific) group: ")

    if short_descr is None:
        short_descr = input("[ ] Short description for the project: ")

    if extern_git_repos is None:
        extern_git_repos = input(
            '[ ] List of external git repositories in the form "name_1|url_1;name_2|url_2": '
        )

    #
    # Get the project metadata
    #

    # Projects location (root dir)
    projects_location = CONFIG_MANAGER["projects.location"]
    if projects_location == "":
        typer.echo(
            typer.style(
                f"Error: SPM has not been configured yet.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Get last used project id
    last_id = MetadataManager.get_last_id(projects_location)

    # Update the id
    project_id = last_id + 1

    # Folder name
    project_dir = f"P_{project_id:04}"

    # Use git?
    use_git = CONFIG_MANAGER["tools.use_git"] == "True"
    git_path = CONFIG_MANAGER["tools.git_path"]

    # Instantiate the project
    project = Project(
        parent_dir=projects_location,
        project_dir=project_dir,
        project_title=title,
        user_name=user_name,
        user_email=user_email,
        user_group=user_group,
        project_short_descr=short_descr,
        use_git=use_git,
        git_path=git_path,
        extern_git_repos=extern_git_repos,
    )

    # Initialize the project
    project.init()

    # Update the last project ID
    MetadataManager.update_last_id(projects_location)

    # Inform
    typer.echo(
        typer.style(
            f"Success! Project '{project.full_path}' was created and initialized.",
            fg=typer.colors.GREEN,
            bold=True,
        )
    )


@app.command("list")
def show():
    """List all projects."""

    # Check that we have a valid configuration
    if not CONFIG_MANAGER.is_valid:
        typer.echo(
            typer.style(
                "Error: spm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        raise typer.Exit()

    # Retrieve the projects table
    project_data, headers = ProjectManager.get_projects(
        CONFIG_MANAGER["projects.location"]
    )

    if len(project_data) == 0:
        typer.echo("No projects found.")
        return
    else:
        table = tabulate(project_data, headers=headers, tablefmt="fancy_grid")
        typer.echo(table)


@app.command("open")
def show():
    """Open the projects folder in the systems file explorer."""

    # Check that we have a valid configuration
    if not CONFIG_MANAGER.is_valid:
        typer.echo(
            typer.style(
                "Error: spm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        raise typer.Exit()

    # Rely on Pythons's `os.startfile()` to open the system's file explorer
    try:
        os.startfile(CONFIG_MANAGER["projects.location"])
    except FileNotFoundError as _:
        typer.echo(
            typer.style(
                f"Error: failed opening folder {CONFIG_MANAGER['projects.location']} in file manager. "
                + f"Please check your configuration.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()
