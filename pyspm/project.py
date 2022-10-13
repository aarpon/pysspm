import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from pyspm.metadata import MetadataParser


class Project:
    """Class Project that takes care of initializing all project information and filesystem structure."""

    def __init__(
        self,
        parent_dir: str,
        project_dir: str,
        project_title: str,
        user_name: str,
        user_email: str,
        user_group: str,
        project_short_descr: str,
        use_git: bool = True,
        git_path: str = "",
        extern_git_repos: str = "",
        extern_data_dir: str = "",
    ):
        """Instantiate a Project object.

        Parameters
        ----------

        parent_dir: str
            Parent folder to the project.

        project_dir: str
            Folder name for the project.

        project_title: str
            Title of the project.

        user_name: str
            User name.

        user_email: str
            User e-mail.

        user_group: str
            User (scientific) group.

        project_short_descr: str
            Short description of the project.

        use_git: bool
            Whether to initialize an empty git repository for the project.

        git_path: str
            Path to the git executable. Leave empty to get it from the path.

        extern_git_repos: str
            List of extern git repositories in the form "name_1|url_1;name_2|url_2". Leave empty to omit.

        extern_data_dir: str
            Optional path to an external data directory.
        """

        self._is_init = False

        # Parent dir (that will contain the project)
        self.PARENT_DIR = Path(parent_dir)

        # Build a folder structure: PARENT_DIR/YEAR/MONTH/PROJECT_DIR
        self.TODAY = date.today()
        self.YEAR = str(self.TODAY.year)
        self.MONTH = str(self.TODAY.month)
        year_path = self.PARENT_DIR / self.YEAR
        month_path = year_path / self.MONTH

        # Project dir
        project_dir = project_dir.replace(" ", "_")
        self.PROJECT_ROOT_DIR = month_path / project_dir

        # Store the input arguments
        self.USER_NAME = user_name
        self.USER_EMAIL = user_email
        self.USER_GROUP = user_group
        self.PROJECT_TITLE = project_title
        self.PROJECT_DESCRIPTION = project_short_descr

        # Build sub-folder structure
        self.METADATA_PATH = self.PROJECT_ROOT_DIR / "metadata"
        self.DATA_PATH = self.PROJECT_ROOT_DIR / "data"
        self.RESULTS_PATH = self.PROJECT_ROOT_DIR / "results"
        self.CODE_PATH = self.PROJECT_ROOT_DIR / "code"
        self.CODE_EXTERN_PATH = self.CODE_PATH / "extern"
        self.CODE_MATLAB_PATH = self.CODE_PATH / "matlab"
        self.CODE_PYTHON_PATH = self.CODE_PATH / "python"
        self.CODE_MACROS_PATH = self.CODE_PATH / "macros"
        self.CODE_NOTEBOOKS_PATH = self.CODE_PATH / "notebooks"
        self.CODE_ILASTIK_PATH = self.CODE_PATH / "ilastik"
        self.REFERENCES_PATH = self.PROJECT_ROOT_DIR / "references"

        # Was there an external data directory specified?
        self.EXTERN_DATA_DIR = ""
        if extern_data_dir != "":
            # Build the same folder structure: EXTERN_DATA_DIR/YEAR/MONTH/PROJECT_DIR
            ext_data_year_path = Path(extern_data_dir).resolve() / self.YEAR
            ext_data_month_path = ext_data_year_path / self.MONTH
            self.EXTERN_DATA_DIR = ext_data_month_path / project_dir

        # Do we use git?
        self.use_git = use_git

        # Extern git repos (submodules)
        self.EXTERN_GIT_REPOS = self._process_list_if_extern_git_repos(extern_git_repos)

        # Find and set path to git executable
        self.git_path = ""
        if git_path == "":
            self._get_and_store_git_path()
        else:
            self.set_git_path(git_path)

    @property
    def full_path(self):
        """Return the full path to the created project."""
        return self.PROJECT_ROOT_DIR

    def init(self):
        """Initialize the project structure.


        Returns
        -------

        result: bool
            True if creation was successful, false otherwise.
        """

        if not os.path.isdir(self.PARENT_DIR):
            os.makedirs(self.PARENT_DIR)

        # If the root folder already exists, we do not want to
        # overwrite anything
        if self.PROJECT_ROOT_DIR.exists():
            print(
                f"The project folder {self.PROJECT_ROOT_DIR} "
                f"already exists. Stopping here."
            )
            return False

        # Create folder structure
        self._create_folder_structure()

        # Write metadata to file
        self._write_metadata_to_file()

        # Write description to a separate file
        self._write_description_to_file()

        # Init git repository
        self._init_git_repo()

        # Add external repos
        self._set_extern_git_projects()

        # Set the init flag
        self._is_init = True

    def set_extern_git_repos(self, extern_git_repos: str):
        """List of git repositories to be added as submodules.

        Parameters
        ----------

        extern_git_repos: str
            List of extern git repositories in the form "name_1|url_1;name_2|url_2". Leave empty to omit.
        """

        if not self._is_init:
            print(
                "The Project must be initialized first. Call Project.init() and try again"
            )
            return

        self.EXTERN_GIT_REPOS = self._process_list_if_extern_git_repos(extern_git_repos)
        self._set_extern_git_projects()

    def set_git_path(self, git_path: str):
        """Explicitly set the path to the git executable to use.

        Parameters
        ----------

        git_path: str
            Full path to the git executable.
        """

        if os.path.isfile(git_path):
            self.git_path = Path(git_path)
        else:
            print(f"File {git_path} does not exist!", file=sys.stderr)

    #
    # Private methods
    #

    def _create_folder_structure(self):
        """Create folder structure."""

        # Create folder structure
        self.PROJECT_ROOT_DIR.mkdir(parents=True, exist_ok=True)
        self.METADATA_PATH.mkdir(parents=True, exist_ok=True)
        self.DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.RESULTS_PATH.mkdir(parents=True, exist_ok=True)
        self.CODE_EXTERN_PATH.mkdir(parents=True, exist_ok=True)
        self.CODE_MATLAB_PATH.mkdir(parents=True, exist_ok=True)
        self.CODE_PYTHON_PATH.mkdir(parents=True, exist_ok=True)
        self.CODE_MACROS_PATH.mkdir(parents=True, exist_ok=True)
        self.CODE_NOTEBOOKS_PATH.mkdir(parents=True, exist_ok=True)
        self.CODE_ILASTIK_PATH.mkdir(parents=True, exist_ok=True)
        self.REFERENCES_PATH.mkdir(parents=True, exist_ok=True)
        if self.EXTERN_DATA_DIR != "":
            self.EXTERN_DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _get_and_store_git_path(self):
        """Try to get and store git's path."""

        if os.name == "nt":
            command = "where"
        else:
            command = "which"

        # Try getting the path to the git executable
        output = subprocess.run(
            [command, "git"], universal_newlines=True, stdout=subprocess.PIPE
        )

        # Was git in the path?
        if output.returncode == 0 and output.stdout != "":
            lines = output.stdout.splitlines()
            if len(lines) > 0:
                git_path = Path(lines[0])
            else:
                git_path = None
        else:
            git_path = None

        self.git_path = git_path

    def _init_git_repo(self):
        """Initialize git repo for project."""

        if not self.use_git:
            return

        if self.git_path == "":
            return

        # Add a .gitignore file
        filename = self.PROJECT_ROOT_DIR / ".gitignore"
        if not filename.is_file():
            # Do not overwrite if it already exists
            with open(filename, "w", encoding="utf-8") as f:
                f.write("/data/\n")
                f.write(".ipynb_checkpoints/")
                f.write("__pycache__/")
                f.write(".pytest_cache/")
                f.write("iaf.egg-info/")
                f.write(".vscode/")
                f.write(".idea/")

        # Init git repo
        curr_path = os.getcwd()
        os.chdir(self.PROJECT_ROOT_DIR)
        subprocess.run(["git", "init"])
        subprocess.run(["git", "config", "core.autocrlf", "false"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", '"Initial import."'])

        # Change back
        os.chdir(curr_path)

    def _process_list_if_extern_git_repos(self, repo_list: str):
        """Process the list of git repos and returns them in a dictionary.

        Parameters
        ----------

        repo_list: str
            List of extern git repositories in the form "name_1|url_1;name_2|url_2". Leave empty to omit.

        Returns
        -------

        repo_dict: dict
            Dictionary in the form { "name_1": "url_1", "name_2": "url_2"}
        """

        # Initialize dictionary
        repo_dict = {}

        # If the list of repositories is empty, return here
        if repo_list == "":
            return repo_dict

        # Split repositories at the ';' separator
        repos = repo_list.split(";")

        for repo in repos:
            parts = repo.split("|")
            if len(parts) == 2:
                repo_dict[parts[0]] = parts[1]
            else:
                print(
                    f"Malformed external repository entry {repo}. Skipping.",
                    file=sys.stderr,
                )

        return repo_dict

    def _set_extern_git_projects(self):
        """Set a list of external git repositories as submodules."""

        curr_path = os.getcwd()

        # Clone extern projects as submodules
        if len(self.EXTERN_GIT_REPOS) > 0:
            os.chdir(self.CODE_EXTERN_PATH)
            for name, url in self.EXTERN_GIT_REPOS.items():
                subprocess.run(["git", "submodule", "add", url, name])
            os.chdir(self.PROJECT_ROOT_DIR)
            subprocess.run(["git", "add", ".gitmodules"])
            subprocess.run(["git", "commit", "-m", '"Add external repositories."'])

        os.chdir(curr_path)

    def _write_metadata_to_file(self):
        """Write metadata to file metadata/metadata.ini."""

        # Store metadata information
        metadata_parser = MetadataParser(self.PROJECT_ROOT_DIR)
        metadata_parser["project.title"] = self.PROJECT_TITLE
        metadata_parser["project.start_date"] = self.TODAY.strftime("%d/%m/%Y")
        metadata_parser["project.end_date"] = ""
        metadata_parser["project.status"] = "new"
        metadata_parser["user.name"] = self.USER_NAME
        metadata_parser["user.email"] = self.USER_EMAIL
        metadata_parser["user.group"] = self.USER_GROUP
        metadata_parser["user.collaborators"] = ""
        metadata_parser.write()

    def _write_description_to_file(self):
        """Write project description to metadata/description.md."""

        # Since the description can be verbose and with formatting,
        # we write it to a comma-separated value file.

        filename = self.METADATA_PATH / "description.md"
        if not filename.is_file():
            # Do not overwrite if it already exists
            with open(filename, "w", encoding="utf-8") as f:
                f.write("# Project description\n")
                f.write(self.PROJECT_DESCRIPTION + "\n")


class ProjectManager(object):
    """Project manager (static class)."""

    @staticmethod
    def get_projects(projects_folder: Path, project_id: Optional[str] = None) -> tuple:
        """Return the list of projects."""

        # Retrieve all sub-folders that map to valid years
        year_folders = ProjectManager._get_year_folders(projects_folder)

        # List to collect project information for rendering
        project_data = []

        # Now process the year folders to extract the months
        for year_folder in year_folders:

            # Extract valid month folders for current year folder
            month_folders = ProjectManager._get_month_folders(year_folder)

            # Now examine all project folders
            for month_folder in month_folders:

                for candidate_project_folder in Path(month_folder).iterdir():

                    if project_id is not None:
                        if project_id not in Path(candidate_project_folder).name:
                            continue

                    metadata_file = (
                        candidate_project_folder / "metadata" / "metadata.ini"
                    )
                    if metadata_file.is_file():
                        try:
                            metadata_parser = MetadataParser(candidate_project_folder)
                            metadata = metadata_parser.read()

                            # Add project data
                            project_data.append(
                                [
                                    year_folder.name,
                                    month_folder.name,
                                    candidate_project_folder.name,
                                    metadata["project.title"],
                                    metadata["user.name"],
                                    metadata["user.email"],
                                    metadata["user.group"],
                                    metadata["project.status"],
                                ]
                            )
                        except Exception as e:
                            print(e)

        headers = [
            "Year",
            "Month",
            "ID",
            "Title",
            "User name",
            "User e-mail",
            "Group",
            "Status",
        ]

        if len(project_data) == 0:
            return None

        return pd.DataFrame(data=project_data, columns=headers)

    @staticmethod
    def get_project_path_by_id(projects_folder: Path, project_id: str) -> str:
        """The project with given ID and returns its full path."""

        # Retrieve all sub-folders that map to valid years
        year_folders = ProjectManager._get_year_folders(projects_folder)

        # Now process the year folders to extract the months
        for year_folder in year_folders:

            # Extract valid month folders for current year folder
            month_folders = ProjectManager._get_month_folders(year_folder)

            # Now examine all project folders
            for month_folder in month_folders:

                for candidate_project_folder in Path(month_folder).iterdir():
                    if project_id in Path(candidate_project_folder).name:
                        return str(Path(candidate_project_folder).resolve())

        # Could not find a project with given `project_id`
        return ""

    @staticmethod
    def _get_year_folders(projects_folder) -> list:
        """Scans the projects folder and returns all valid year folders."""

        year_subfolders = []
        for subfolder in Path(projects_folder).iterdir():
            try:
                year = int(subfolder.name)
                if year < 2021:
                    raise ValueError("Only years after 2021 are valid.")
            except ValueError as _:
                # Ignore the error and move on
                continue

            year_subfolders.append(subfolder)

        return year_subfolders

    @staticmethod
    def _get_month_folders(year_folder) -> list:
        """Scans the year folder and returns all valid months folders."""

        month_subfolders = []
        for subfolder in Path(year_folder).iterdir():
            try:
                month = int(subfolder.name)
                if month < 0 or month > 12:
                    raise ValueError(
                        "Only integer representing months (1..12) are valid."
                    )
            except ValueError as _:
                # Ignore the error and move on
                continue

            month_subfolders.append(subfolder)

        return month_subfolders
