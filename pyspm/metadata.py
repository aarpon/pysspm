import configparser
from pathlib import Path
from typing import Union


class MetadataParser:
    """Project metadata (singleton class)."""

    def __init__(self, project_folder: Union[Path, str]):
        """Constructor.

        The MetadataParser loads the metadata file if it exists or creates
        a default one that is not yet usable.
        """

        # Current version
        self._version = 1

        # Valid keys
        self.valid_keys = [
            "metadata.version",
            "project.title",
            "project.start_date",
            "project.end_date",
            "project.status",
            "project.description",
            "user.name",
            "user.email",
            "user.group",
            "user.collaborators",
        ]

        # Configuration parser
        self._metadata = None

        # Metadata folder
        self._metadata_path = Path(project_folder) / "metadata"

        # Metadata file name
        self._metadata_file = self._metadata_path / "metadata.ini"

        # If the metadata file does not exist yet, create a default one
        if not self._metadata_file.is_file():
            self._write_default()

        # Read it
        if self._metadata is None:
            self._metadata = configparser.ConfigParser()
        self._metadata.read(self._metadata_file)

    def __getitem__(self, item):
        """Get item for current key."""
        parts = item.split(".")
        if parts[0] not in self._metadata.sections():
            raise ValueError(f"Invalid metadata key '{item}'.")
        if parts[1] not in self._metadata[parts[0]]:
            raise ValueError(f"Invalid metadata key '{item}'.")
        return self._metadata[parts[0]][parts[1]]

    def __setitem__(self, item, value):
        """Set value for requested item."""

        # Find the correct keys
        parts = item.split(".")
        if parts[0] not in self._metadata.sections():
            raise ValueError(f"Invalid metadata key '{item}'.")
        if parts[1] not in self._metadata[parts[0]]:
            raise ValueError(f"Invalid metadata key '{item}'.")
        self._metadata[parts[0]][parts[1]] = value

        # Write the metadata file
        with open(self._metadata_file, "w", encoding="utf-8") as metadataFile:
            self._metadata.write(metadataFile)

    @property
    def metadata_file(self) -> str:
        """Return full path of metadata file."""
        return str(self._metadata_file)

    @property
    def is_valid(self) -> bool:
        """Check current metadata values."""
        return self._validate()

    def keys(self) -> list:
        """Return the list of metadata keys."""
        return self.valid_keys

    def write(self) -> bool:
        """Save the metadata file."""

        # Initialize the configuration parser
        if self._metadata is None:
            return False

        # Make sure the metadata folder exists
        Path(self._metadata_path).mkdir(exist_ok=True)

        # Write the metadata file
        with open(self._metadata_file, "w", encoding="utf-8") as metadataFile:
            self._metadata.write(metadataFile)

    def _validate(self):
        """Check current metadata values."""

        # Check that the version matches the latest
        if self._metadata["metadata"]["version"] != str(self._version):
            return False

        # Mandatory entries must be set (validation is performed elsewhere)
        if self._metadata["project"]["title"] == "":
            return False
        if self._metadata["user"]["name"] == "":
            return False
        if self._metadata["user"]["email"] == "":
            return False
        if self._metadata["user"]["group"] == "":
            return False

        return True

    def _write_default(self):
        """Write default metadata file."""

        # Initialize the configuration parser
        if self._metadata is None:
            self._metadata = configparser.ConfigParser()

        # Metadata information
        self._metadata["metadata"] = {}
        self._metadata["metadata"]["version"] = str(self._version)

        # Project
        self._metadata["project"] = {}
        self._metadata["project"]["title"] = ""
        self._metadata["project"]["start_date"] = ""
        self._metadata["project"]["end_date"] = ""
        self._metadata["project"]["status"] = ""
        self._metadata["project"]["description"] = ""

        # User
        self._metadata["user"] = {}
        self._metadata["user"]["name"] = ""
        self._metadata["user"]["email"] = "True"
        self._metadata["user"]["group"] = "True"
        self._metadata["user"]["collaborators"] = "True"

        # Make sure the metadata folder exists
        Path(self._metadata_path).mkdir(exist_ok=True)

        # Write the metadata file
        with open(self._metadata_file, "w", encoding="utf-8") as metadataFile:
            self._metadata.write(metadataFile)
