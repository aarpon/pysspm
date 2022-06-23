import os
import subprocess
import sys
from datetime import date
from pathlib import Path


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
            with open(filename, "w") as f:
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
        """Write metadata to file metadata/info.md."""

        # Add some simple metadata information
        filename = self.METADATA_PATH / "info.md"
        if not filename.is_file():
            # Do not overwrite if it already exists
            with open(filename, "w") as f:
                f.write("# " + self.PROJECT_TITLE + "\n")
                f.write("**Start date**: " + self.TODAY.strftime("%d/%m/%Y") + "\n")
                f.write("**End date**:\n")
                f.write("## User information\n")
                f.write("**Name**: " + self.USER_NAME + "\n")
                f.write("**E-mail**: " + self.USER_EMAIL + "\n")
                f.write("**Group**: " + self.USER_GROUP + "\n")
                f.write("**Collaborators**: \n\n")
                f.write("## Description\n")
                f.write(self.PROJECT_DESCRIPTION + "\n")