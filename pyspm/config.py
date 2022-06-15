import configparser
from pathlib import Path

from pyspm.util import Singleton


class ConfigurationManager(object, metaclass=Singleton):
    """Configuration manager (singleton class)."""

    def __init__(self):
        """Constructor.

        The ConfigurationManager loads the configuration file if it exists or creates
        a default one that is not yet usable.
        """

        # Current version
        self._version = 0

        # Valid keys
        self.valid_keys = [
            "projects.location",
            "tools.git_path"
        ]

        # Configuration parser
        self._config = None

        # Configuration folder
        self._conf_path = Path(Path.home(), ".config/pyspm")

        # Config file name
        self._conf_file = self._conf_path / "pyspm.ini"

        # If the configuration file does not exist yet, create a default one
        if not self._conf_file.is_file():
            self._write_default()

        # Read it
        if self._config is None:
            self._config = configparser.ConfigParser()
        self._config.read(self._conf_file)

    def __getitem__(self, item):
        """Get item for current key."""
        parts = item.split(".")
        if parts[0] not in self._config.sections():
            raise ValueError(f"Invalid configuration key '{item}'.")
        if parts[1] not in self._config[parts[0]]:
            raise ValueError(f"Invalid configuration key '{item}'.")
        return self._config[parts[0]][parts[1]]

    @property
    def is_valid(self) -> bool:
        """Check current configuration."""
        return self._validate()

    def keys(self) -> list:
        """Return the list of configuration keys."""
        return self.valid_keys

    def _validate(self):
        """Check current configuration."""

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

        # Tools
        self._config["tools"] = {}
        self._config["tools"]["git_path"] = ""

        # Make sure the .config/obit folder exists
        Path(self._conf_path).mkdir(exist_ok=True)

        # Write the configuration file
        with open(self._conf_file, "w") as configfile:
            self._config.write(configfile)
