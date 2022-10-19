import os
import platform
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from tabulate import tabulate

from pyspm.config import ConfigurationParser, GlobalMetadataManager
from pyspm.metadata import MetadataParser
from pyspm.project import Project, ProjectManager

# Load configuration (singleton)
CONFIG_PARSER = ConfigurationParser()

# Instantiate Typer
app = typer.Typer(name="project", help="Manage projects.")


@app.command("create")
def create(
    title: str = typer.Option(default=None, help="Title of the project."),
    user_name: str = typer.Option(default=None, help="User's first and family name."),
    user_email: str = typer.Option(default=None, help="User's e-mail address."),
    user_group: str = typer.Option(default=None, help="User's group."),
    short_descr: str = typer.Option(
        default=None, help='Short description of the project. Set to "" to skip.'
    ),
    extern_git_repos: str = typer.Option(
        default=None,
        help='List of remote git repositories in the form "name_1|url_1;name_2|url_2". '
             'Not interactive: explicitly pass to set.',
    ),
):
    """Create a new project. Just call `spm project create` for interactive input."""

    # Check that we have a valid configuration
    if not CONFIG_PARSER.is_valid:
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
        extern_git_repos = ""

    #
    # Get the project metadata
    #

    # Projects location (root dir)
    projects_location = CONFIG_PARSER["projects.location"]
    if projects_location == "":
        typer.echo(
            typer.style(
                f"Error: SPM has not been configured yet.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Extern data dir
    extern_data_dir = CONFIG_PARSER["projects.external_data"]

    # Get last used project id
    last_id = GlobalMetadataManager.get_last_id(projects_location)

    # Update the id
    project_id = last_id + 1

    # Folder name
    project_dir = f"P_{project_id:04}"

    # Use git?
    use_git = CONFIG_PARSER["tools.use_git"] == "True"
    git_path = CONFIG_PARSER["tools.git_path"]
    git_ignore_data = CONFIG_PARSER["tools.git_ignore_data"] == "True"

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
        git_ignore_data=git_ignore_data,
        extern_data_dir=extern_data_dir,
    )

    # Initialize the project
    project.init()

    # Update the last project ID
    GlobalMetadataManager.update_last_id(projects_location)

    # Inform
    typer.echo(
        typer.style(
            f"Success! Project '{project.full_path}' was created and initialized.",
            fg=typer.colors.GREEN,
            bold=True,
        )
    )


@app.command("list")
def show(
    project_id: Optional[str] = typer.Argument(
        None, help="ID of the project to visualize. Omit to show all projects."
    )
):
    """List all projects."""

    # Check that we have a valid configuration
    if not CONFIG_PARSER.is_valid:
        typer.echo(
            typer.style(
                "Error: spm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        raise typer.Exit()

    # Retrieve the projects table
    project_dataframe = ProjectManager.get_projects(
        CONFIG_PARSER["projects.location"], project_id
    )

    if project_dataframe is None:
        typer.echo("No projects found.")
        return
    else:
        table = tabulate(
            project_dataframe,
            headers=project_dataframe.columns,
            showindex=False,
            tablefmt="fancy_grid",
        )
        typer.echo(table)


@app.command("open")
def open_folder(
    project_id: Optional[str] = typer.Argument(
        None,
        help="ID of the project folder to open. Omit to open the root projects folder.",
    )
):
    """Open a requested or all projects folder in the system's file explorer."""

    # Check that we have a valid configuration
    if not CONFIG_PARSER.is_valid:
        typer.echo(
            typer.style(
                "Error: spm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        raise typer.Exit()

    if project_id is None:
        folder_to_open = CONFIG_PARSER["projects.location"]
    else:
        folder_to_open = ProjectManager.get_project_path_by_id(
            CONFIG_PARSER["projects.location"], project_id
        )

    # Project not found. Inform and return
    if folder_to_open == "":
        typer.echo(
            typer.style(
                f"Error: could not find a folder for project {project_id}. "
                + f"Make sure to spell the complete ID.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Inform
    typer.echo(
        typer.style(
            f"Opening {folder_to_open}. ",
            fg=typer.colors.GREEN,
            bold=True,
        )
    )

    if platform.system() == "Windows":
        try:
            os.startfile(folder_to_open)
        except FileNotFoundError as _:
            typer.echo(
                typer.style(
                    f"Error: failed opening folder {folder_to_open} in Windows explorer. "
                    + f"Please check your configuration.",
                    fg=typer.colors.RED,
                    bold=True,
                )
            )
            raise typer.Exit()

    elif platform.system() == "Darwin":
        try:
            subprocess.call(["open", folder_to_open])
        except FileNotFoundError as _:
            typer.echo(
                typer.style(
                    f"Error: failed opening folder {folder_to_open} in Finder. "
                    + f"Please check your configuration.",
                    fg=typer.colors.RED,
                    bold=True,
                )
            )
            raise typer.Exit()

    elif platform.system() == "Linux":
        try:
            subprocess.call(["xdg-open", folder_to_open])
        except FileNotFoundError as _:
            typer.echo(
                typer.style(
                    f"Error: failed opening folder {folder_to_open} in Finder. "
                    + f"Please check your configuration.",
                    fg=typer.colors.RED,
                    bold=True,
                )
            )
            raise typer.Exit()

    else:
        typer.echo(
            typer.style(
                f"Sorry, your platform is not supported.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()


@app.command("close")
def close_project(
    project_id: str = typer.Argument(
        None,
        help="ID of the project to close.",
    ),
    mode: str = typer.Argument(
        "now",
        help='How to close the project. One of "now" or "latest".',
    ),
):
    """Close the requested project either \"now\" or at the date of the \"latest\" modification.

    The `project.end_date` property will be set to the requested date, and the `project.status` property
    will be set to `completed`.
    """

    if mode not in ["now", "latest"]:
        typer.echo(
            typer.style(
                f'Error: "mode" must be one of "now" or "latest".',
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Check that we have a valid configuration
    if not CONFIG_PARSER.is_valid:
        typer.echo(
            typer.style(
                "Error: spm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        raise typer.Exit()

    # Get the full path to the requested project ID.
    project_folder = ProjectManager.get_project_path_by_id(
        CONFIG_PARSER["projects.location"], project_id
    )

    # Project not found. Inform and return
    if project_folder == "":
        typer.echo(
            typer.style(
                f"Error: could not find a folder for project {project_id}. "
                + f"Make sure to spell the complete ID.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    try:
        ProjectManager.close(project_folder, mode)
    except Exception as e:
        typer.echo(
            typer.style(
                f"Error: could not close project with ID {project_id}. "
                + f"Error was: {e}",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()


@app.command("get")
def get_metadata(
    project_id: str = typer.Argument(default=None, help="ID of the project to query."),
    metadata_key: str = typer.Argument(
        default="project.title", help="Key of the metadata value to retrieve."
    ),
):
    """Get value for the requested metadata key of given project."""

    # Project not found. Inform and return
    if project_id is None:
        typer.echo(
            typer.style(
                f"Error: please specify the ID of the project to query.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Check that we have a valid configuration
    if not CONFIG_PARSER.is_valid:
        typer.echo(
            typer.style(
                "Error: spm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        raise typer.Exit()

    # Try to find the requested project
    project_folder = ProjectManager.get_project_path_by_id(
        CONFIG_PARSER["projects.location"], project_id
    )

    # Project not found. Inform and return
    if project_folder == "":
        typer.echo(
            typer.style(
                f"Error: could not find a folder for project {project_id}. "
                + f"Make sure to spell the complete ID.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Now initialize the metadata parser
    metadata_parser = MetadataParser(project_folder)

    # Try to get the requested metadata value
    try:
        metadata_value = metadata_parser[metadata_key]
        typer.echo(f"{metadata_value}")
    except ValueError as _:
        valid_keys = metadata_parser.keys
        valid_keys.remove("metadata.version")
        typer.echo(
            typer.style(
                f"Error: the specified metadata key '{metadata_key}' is not recognized. "
                f"Valid metadata keys are {metadata_parser.keys}",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()


@app.command("set")
def set_metadata(
    project_id: str = typer.Argument(default=None, help="ID of the project to query."),
    metadata_key: str = typer.Argument(
        default="project.title", help="Key of the metadata value to retrieve."
    ),
    metadata_value: str = typer.Argument(
        default="", help="Value for the specified metadata key."
    ),
):
    """Set value for the specified metadata key of given project."""

    # Project not found. Inform and return
    if project_id is None:
        typer.echo(
            typer.style(
                f"Error: please specify the ID of the project to query.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Check that we have a valid configuration
    if not CONFIG_PARSER.is_valid:
        typer.echo(
            typer.style(
                "Error: spm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
        raise typer.Exit()

    # Try to find the requested project
    project_folder = ProjectManager.get_project_path_by_id(
        CONFIG_PARSER["projects.location"], project_id
    )

    # Project not found. Inform and return
    if project_folder == "":
        typer.echo(
            typer.style(
                f"Error: could not find a folder for project {project_id}. "
                + f"Make sure to spell the complete ID.",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Now initialize the metadata parser
    metadata_parser = MetadataParser(project_folder)

    # Can the value be empty?
    if metadata_value == "" and not metadata_parser.can_be_empty(metadata_key):
        typer.echo(
            typer.style(
                f"Error: the metadata key {metadata_key} can not be set to empty!",
                fg=typer.colors.RED,
                bold=True,
            )
        )
        raise typer.Exit()

    # Try to set the requested metadata value
    try:
        metadata_parser[metadata_key] = metadata_value
    except ValueError as e:
        typer.echo(
            typer.style(
                f"Error: could not set metadata key '{metadata_key}'. "
                f"The error was: {e}"
            )
        )
        raise typer.Exit()
