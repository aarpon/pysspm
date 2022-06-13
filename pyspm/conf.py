import configparser
from pathlib import Path


class ConfigurationManager(object):
    """Configuration manager."""

    def __init__(self):
        """Constructor.

        The ConfigurationManager loads the configuration file if it exists or creates
        a default one that is not yet usable.
        """

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

    @property
    def is_valid(self) -> bool:
        """Check current configuration."""
        return self._validate()

    def _validate(self):
        """Check current configuration."""
        print("Implement config file validation!")

        return False

    def _write_default(self):
        """Write default configuration file."""

        # Initialize the configuration parser
        if self._config is None:
            self._config = configparser.ConfigParser()

        # Metadata information
        self._config["metadata"] = {}
        self._config["metadata"]["version"] = "0"

        # Projects root folder
        self._config["projects"] = {}
        self._config["projects"]["location"] = ""

        # Make sure the .config/obit folder exists
        Path(self._conf_path).mkdir(exist_ok=True)

        # Write the configuration file
        with open(self._conf_file, "w") as configfile:
            self._config.write(configfile)
