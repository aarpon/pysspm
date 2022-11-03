import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from .metadata import MetadataParser

__doc__ = "Internal classes and functions to manage projects."


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
        git_ignore_data: bool = True,
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

        git_ignore_data: bool
            Whether to add the data folder to .gitignore.

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

        # Should we ignore the data folder?
        self.git_ignore_data = git_ignore_data

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

    def set_git_path(self, git_path: Union[Path, str]):
        """Explicitly set the path to the git executable to use.

        Parameters
        ----------

        git_path: str
            Full path to the git executable.
        """

        git_path = Path(git_path)
        if git_path.isfile():
            self.git_path = git_path
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
                if self.git_ignore_data:
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
    def keys() -> list:
        """Return editable keys.

        Returns
        -------

        keys: list
            List if editable project keys.
        """
        return [
            "project.title",
            "user.name",
            "user.email",
            "user.group",
            "project.start_date",
            "project.end_date",
            "project.status",
        ]

    @staticmethod
    def get_projects(
        projects_folder: Union[Path, str],
        project_id: Optional[str] = None,
        detailed: bool = False,
    ) -> Union[None, pd.DataFrame]:
        """Return the metadata of either all projects, or the project with specified `project_id`.

        Parameters
        ----------

        projects_folder: Path
            Path to the root of the projects folder.

        project_id: str
            Project ID (or a univocal substring) for which to return metadata. Omit to return the metadata of all projects.

        detailed: bool
            Whether to return complete metadata or a subset.

        Returns
        -------

        metadata: Union[None|pd.Dataframe]
            Dataframe containing project metadata or None if the requested `project_id` could not be found.
        """

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
                            if detailed:
                                project_data.append(
                                    [
                                        int(year_folder.name),
                                        int(month_folder.name),
                                        candidate_project_folder.name,
                                        metadata["project.title"],
                                        metadata["user.name"],
                                        metadata["user.email"],
                                        metadata["user.group"],
                                        metadata["project.start_date"],
                                        metadata["project.end_date"],
                                        metadata["project.status"],
                                    ]
                                )
                            else:
                                project_data.append(
                                    [
                                        int(year_folder.name),
                                        int(month_folder.name),
                                        candidate_project_folder.name,
                                        metadata["project.title"],
                                        metadata["user.name"],
                                        metadata["user.group"],
                                        metadata["project.status"],
                                    ]
                                )
                        except Exception as e:
                            print(e)

        if detailed:
            headers = [
                "Year",
                "Month",
                "ID",
                "Title",
                "User name",
                "User e-mail",
                "Group",
                "Start date",
                "End date",
                "Status",
            ]
        else:
            headers = [
                "Year",
                "Month",
                "ID",
                "Title",
                "User name",
                "Group",
                "Status",
            ]

        if len(project_data) == 0:
            return None

        df = pd.DataFrame(data=project_data, columns=headers)
        df.sort_values(
            by=["Year", "Month", "ID"], ascending=True, inplace=True, ignore_index=True
        )

        if not detailed:
            df = df.drop(["Year", "Month"], axis=1)

        return df

    @staticmethod
    def get_project_path_by_id(projects_folder: Path, project_id: str) -> str:
        """Returns the full path to the project with given `project_id`.

        Parameters
        ----------

        projects_folder: Path
            Path to the root of the projects folder.

        project_id: str
            Project ID (or a univocal substring) for which to return the project full path.

        Returns
        -------

        project_path: str
            String containing the project full path or "" if the project could not be found.
        """

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
    def get_external_data_path_by_id(
        external_data_folder: Path, project_id: str
    ) -> str:
        """Returns the full path to external data folder for project with given `project_id`.

        Parameters
        ----------

        external_data_folder: Path
            Path to the root of the external data folder.

        project_id: str
            Project ID (or a univocal substring) for which to return the external data folder full path.

        Returns
        -------

        external_data_path: str
            String containing the full path or "" if the data folder for the project could not be found.
        """

        # Retrieve all sub-folders that map to valid years
        year_folders = ProjectManager._get_year_folders(external_data_folder)

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
    def close(project_folder: Union[Path, str], mode: str = "now") -> str:
        """Close the specified project, either \"now\" or at the date of the \"latest\" file modification.

        Parameters
        ----------

        project_folder: Path
            Full path to the project to close. A project is closed by setting its `project.status` (to
            `completed`I and `project.end_date`.

        mode: str
            One of two modes of setting the closing date: if "now", today's date will be used; if "latest",
            the date of the last modification date find in the whole folder (excluding metadata and git
            information). In both cases, date will be in the form DD/MM/YYYY.

        Returns
        -------

        closing_date: str
            String containing the closing date in the form DD/MM/YYYY.
        """

        if mode not in ["now", "latest"]:
            raise ValueError('"mode" must be one of "now" or "latest".')

        if not Path(project_folder).is_dir():
            raise IOError(f"Path {project_folder} does not exist.")

        if mode == "now":
            closing_date = datetime.now().strftime("%d/%m/%Y")
        else:
            last_m_time = ProjectManager._get_last_modification_time(project_folder)
            if last_m_time == -1:
                # No files found to extract last modification date
                raise IOError("No files found to extract last modification date.")
            closing_date = datetime.fromtimestamp(last_m_time).strftime("%d/%m/%Y")

        # Get the metadata of this project
        metadata_parser = MetadataParser(project_folder)

        # Close the project with this date
        metadata_parser["project.end_date"] = closing_date
        metadata_parser["project.status"] = "completed"

        # Return the closing data
        return closing_date

    @staticmethod
    def _get_year_folders(projects_folder: Union[Path, str]) -> list[Path]:
        """Scans the projects folder and returns the paths of all valid year subfolders.

        Parameters
        ----------

        projects_folder: Path
            Path to the root of the projects folder.

        Returns
        -------

        year_subfolders: list[Path]
            List of full paths to the years subfolders.
        """

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
    def _get_month_folders(year_folder: Union[Path, str]) -> list[Path]:
        """Scans the year folder and returns the paths of all valid months subfolders.

        Parameters
        ----------

        year_folder: Path
            Full Path to a year subfolder.

        Returns
        -------

        month_subfolders: list[Path]
            List of full paths to the month subfolders.

        """

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

    @staticmethod
    def _get_last_modification_time(project_folder: Union[Path, str]) -> int:
        """Return the last modification time from all file in given project folder.

        Parameters
        ----------

        project_folder: Union[Path, str]
            Full path to the project to scan.

        Returns
        -------

        last_m_time: int
            Last modification time as returned from `os.stat(file).st_mtime`.
        """

        if not Path(project_folder).is_dir():
            raise IOError(f"Path {project_folder} does not exist.")

        # Exclude .git folder and metadata.ini file
        folder_exclude = [".git"]
        file_exclude = ["metadata.ini"]

        last_m_time = -1
        for root, dirs, files in os.walk(
            project_folder, topdown=True, onerror=None, followlinks=False
        ):
            dirs[:] = [d for d in dirs if d not in folder_exclude]
            for f in files:
                if Path(os.path.join(root, f)).name in file_exclude:
                    continue
                m_time = os.stat(os.path.join(root, f)).st_mtime
                if m_time > last_m_time:
                    last_m_time = m_time

        return last_m_time
