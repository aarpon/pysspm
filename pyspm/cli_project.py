import re
from pathlib import Path

import typer

from pyspm.config import ConfigurationManager

# Load configuration (singleton)
from pyspm.project import Project

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

    # Current project id
    project_id = CONFIG_MANAGER.next_id

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
    CONFIG_MANAGER.update_id()

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

    # Retrieve all subfolders that map to valid years
    valid_years_subfolders = {}
    for subfolder in Path(CONFIG_MANAGER["projects.location"]).iterdir():
        try:
            year = int(subfolder.name)
            if year < 2021:
                raise ValueError("Only years after 2021 are valid.")
        except ValueError as _:
            continue

        valid_years_subfolders[subfolder] = []

    # Now process the years subfolders to extract the months
    for year_subfolder in valid_years_subfolders:
        print(year_subfolder.name)
        valid_months_subfolders = []
        for subfolder in Path(year_subfolder).iterdir():
            try:
                month = int(subfolder.name)
                if month < 0 or month > 12:
                    raise ValueError(
                        "Only integer representing months (1..12) are valid."
                    )
            except ValueError as _:
                continue

            valid_months_subfolders.append(subfolder)

        for valid_month in valid_months_subfolders:
            print(f"\t{valid_month.name}")
            for subfolder in Path(valid_month).iterdir():
                metadata_file = subfolder / "metadata" / "info.md"
                if metadata_file.is_file():
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            title = ""
                            user = ""
                            group = ""
                            status = ""
                            for line in f:
                                line = line.strip()
                                if line.startswith("# "):
                                    title = line[2:].strip()
                                if line.startswith("**Status**: "):
                                    status = line[12:]
                                if line.startswith("**Name**: "):
                                    user = line[10:]
                                if line.startswith("**Group**: "):
                                    group = line[11:]
                                if (
                                    title != ""
                                    and status != ""
                                    and user != ""
                                    and group != ""
                                ):
                                    break
                            typer.echo(
                                f"\t\t[{subfolder.name}] {user} ({group}):: {title} [{status}]"
                            )
                    except Exception as e:
                        print(e)
