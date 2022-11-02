import configparser
import shutil
from datetime import datetime
from pathlib import Path

from .util import Singleton

__doc__ = "Internal classes and functions to manage configuration options."


class ConfigurationParser(object, metaclass=Singleton):
    """Configuration parser (singleton class)."""

    def __init__(self):
        """Constructor.

        The ConfigurationParser loads the configuration file if it exists or creates
        a default one that is not yet usable.
        """

        # Current version
        self._version = 1

        # Valid keys
        self.valid_keys = [
            "projects.location",
            "projects.external_data",
            "tools.git_path",
            "tools.use_git",
            "tools.git_ignore_data",
        ]

        # Configuration keys that can have empty value
        self.valid_empty_keys = [
            "projects.external_data",
            "tools.git_path",
        ]

        # Configuration parser
        self._config = None

        # Configuration folder
        self._conf_path = Path(Path.home(), ".config/pysspm")

        # Config file name
        self._conf_file = self._conf_path / "pysspm.ini"

        # If the configuration file does not exist yet, create a default one
        if not self._conf_file.is_file():
            self._write_default()

        # Read it
        if self._config is None:
            self._config = configparser.ConfigParser()
        self._config.read(self._conf_file, encoding="utf-8")

    def reset(self):
        """Reset the configuration to default values."""
        if self._conf_file.is_file():
            timestamp = datetime.strftime(datetime.now(), "%d%m%Y_%H%M%S")
            backup_file_name = (
                self._conf_file.parent / f"{self._conf_file.stem}_{timestamp}.ini"
            )
            shutil.copyfile(self._conf_file, backup_file_name)
        self._write_default()

    def __getitem__(self, key: str) -> str:
        """Get value for current key.

        Parameters
        ----------

        key: str
            Key to be queried.

        Returns
        -------

        value: str
            Value associated to requested key.
        """
        parts = key.split(".")
        if parts[0] not in self._config.sections():
            raise ValueError(f"Invalid configuration key '{key}'.")
        if parts[1] not in self._config[parts[0]]:
            raise ValueError(f"Invalid configuration key '{key}'.")
        return self._config[parts[0]][parts[1]]

    def __setitem__(self, key: str, value: str):
        """Set value for requested key.

        Parameters
        ----------

        key: str
            Key to be updated.

        value: str
            Value to be associated to the requested key.
        """

        # Find the correct keys
        parts = key.split(".")
        if parts[0] not in self._config.sections():
            raise ValueError(f"Invalid configuration key '{key}'.")
        if parts[1] not in self._config[parts[0]]:
            raise ValueError(f"Invalid configuration key '{key}'.")
        if value == "" and not self.can_be_empty(key):
            raise ValueError(f"Key {key} can not be set to ''.")
        self._config[parts[0]][parts[1]] = value

        # Write the configuration file
        with open(self._conf_file, "w", encoding="utf-8") as configfile:
            self._config.write(configfile)

    @property
    def config_file(self) -> str:
        """Return full path of configuration file.

        Returns
        -------

        conf_file: str
            Full path to the configuration file.
        """
        return str(self._conf_file)

    @property
    def is_valid(self) -> bool:
        """Check current configuration.

        Returns
        -------

        is_valid: bool
            True if the configuration file is valid, False otherwise.
        """
        return self._validate()

    def keys(self) -> list:
        """Return the list of configuration keys.

        Returns
        -------

        keys: list[str]
            List of configuration keys.
        """
        return self.valid_keys

    def can_be_empty(self, key) -> bool:
        """Return True if requested configuration key can be set to empty.

        Parameters
        ----------

        key: str
            Key for which to query whether it can be empty.

        Returns
        -------

        result: bool
            True if the requested configuration key can have value = "".
        """

        if key not in self.valid_keys:
            raise ValueError("The requested configuration key is not recognized.")

        if key in self.valid_empty_keys:
            return True

        return False

    def _validate(self) -> bool:
        """Check current configuration.

        Returns
        -------

        is_valid: bool
           True if the metadata file is valid, False otherwise.
        """

        # Check that the version matches the latest
        if self._config["metadata"]["version"] != str(self._version):
            return False

        # Check that the Projects location value is set
        if self._config["projects"]["location"] == "":
            return False

        location = Path(self._config["projects"]["location"])
        location.mkdir(parents=True, exist_ok=True)
        if location.is_dir():
            return True

        return False

    def _write_default(self):
        """Write default configuration file."""

        # Initialize the configuration parser
        if self._config is None:
            self._config = configparser.ConfigParser()

        # Metadata information
        self._config["metadata"] = {}
        self._config["metadata"]["version"] = str(self._version)

        # Projects root folder
        self._config["projects"] = {}
        self._config["projects"]["location"] = ""
        self._config["projects"]["external_data"] = ""

        # Tools
        self._config["tools"] = {}
        self._config["tools"]["git_path"] = ""
        self._config["tools"]["use_git"] = "True"
        self._config["tools"]["git_ignore_data"] = "True"

        # Make sure the .config/obit folder exists
        Path(self._conf_path).mkdir(exist_ok=True)

        # Write the configuration file
        with open(self._conf_file, "w", encoding="utf-8") as configfile:
            self._config.write(configfile)


class GlobalMetadataManager(object):
    """Project metadata manager (static class)."""

    @staticmethod
    def get_last_id(projects_folder: Path) -> int:
        """Get the last project id.

        Parameters
        ----------

        projects_folder: Path
            Path to the root of the projects folder.

        Returns
        -------

        last_id: int
            Numeric ID of the mpst recent project.
        """
        projects_metadata = Path(projects_folder) / ".projects"
        if not projects_metadata.is_file():
            with open(projects_metadata, "w", encoding="utf-8") as f:
                f.write("last_id=-1")
        with open(projects_metadata, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if not line.startswith("last_id="):
                raise ValueError(f"The file {projects_metadata} is corrupted!")
            try:
                last_id = int(line[8:])
            except ValueError as _:
                raise ValueError(f"The file {projects_metadata} is corrupted!")
        return last_id

    @staticmethod
    def update_last_id(projects_folder: Path) -> None:
        """Update the last project id.

        Parameters
        ----------

        projects_folder: Path
            Path to the root of the projects folder.
        """

        # Get the last id
        last_id = GlobalMetadataManager.get_last_id(projects_folder)
        next_id = last_id + 1
        projects_metadata = Path(projects_folder) / ".projects"
        with open(projects_metadata, "w", encoding="utf-8") as f:
            f.write(f"last_id={next_id}")
