import configparser
from pathlib import Path
from typing import Union

__doc__ = "Internal classes and functions to manage project metadata."


class MetadataParser:
    """Project metadata (singleton class)."""

    def __init__(self, project_folder: Union[Path, str]):
        """Constructor.

        The MetadataParser loads the metadata file if it exists or creates
        a default one that is not yet usable.

        Parameters
        ----------

        project_folder: Union[Path, str]
            Full path to the project to scan.
        """

        # Current version
        self._version = 1

        # Valid keys
        self.valid_keys = [
            "project.title",
            "project.start_date",
            "project.end_date",
            "project.status",
            "user.name",
            "user.email",
            "user.group",
            "user.collaborators",
        ]

        # Metadata keys that can have empty value
        self.valid_empty_keys = ["user.collaborators", "project.end_date"]

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
        self._metadata.read(self._metadata_file, encoding="utf-8")

    def __getitem__(self, key) -> str:
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
        if parts[0] not in self._metadata.sections():
            raise ValueError(f"Invalid metadata key '{key}'.")
        if parts[1] not in self._metadata[parts[0]]:
            raise ValueError(f"Invalid metadata key '{key}'.")
        return self._metadata[parts[0]][parts[1]]

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
        if parts[0] not in self._metadata.sections():
            raise ValueError(f"Invalid metadata key '{key}'.")
        if parts[1] not in self._metadata[parts[0]]:
            raise ValueError(f"Invalid metadata key '{key}'.")
        if value == "" and not self.can_be_empty(key):
            raise ValueError(f"Key {key} can not be set to ''.")
        # Set the value for the requested item
        self._metadata[parts[0]][parts[1]] = value

        # Write the metadata file
        with open(self._metadata_file, "w", encoding="utf-8") as metadataFile:
            self._metadata.write(metadataFile)

    @property
    def metadata_file(self) -> str:
        """Return full path of metadata file.

        Returns
        -------

        metadata_file: str
            Full path to the metadata.ini file.
        """
        return str(self._metadata_file)

    @property
    def is_valid(self) -> bool:
        """Check current metadata values.

        Returns
        -------

        is_valid: bool
            True if the metadata file is valid, False otherwise.
        """
        return self._validate()

    @property
    def keys(self) -> list[str]:
        """Return the list of metadata keys.

        Returns
        -------

        keys: list[str]
            List of metadata keys.
        """
        return self.valid_keys

    def can_be_empty(self, key) -> bool:
        """Return True if requested metadata can be set to empty.

        Parameters
        ----------

        key: str
            Key for which to query whether it can be empty.

        Returns
        -------

        result: bool
            True if the requested metadata key can have value = "".
        """

        if key not in self.valid_keys:
            raise ValueError("The requested metadata key is not recognized.")

        if key in self.valid_empty_keys:
            return True

        return False

    def read(self) -> dict:
        """Read the metadata file.

        Returns
        -------

        metadata_dict: dict
            Dictionary of all metadata key-value pairs.
        """

        # Read it
        if self._metadata is None:
            return {}
        self._metadata.read(self._metadata_file, encoding="utf-8")

        metadata_dict = {}
        for section in self._metadata.sections():
            if section == "metadata":
                continue
            for option in self._metadata[section]:
                key = f"{section}.{option}"
                metadata_dict[key] = self._metadata[section][option]
        return metadata_dict

    def write(self) -> bool:
        """Save the metadata file.

        Returns
        -------

        result: bool
            True if the metadata file could be written successfully, False otherwise.
        """

        # Initialize the configuration parser
        if self._metadata is None:
            return False

        # Make sure the metadata folder exists
        Path(self._metadata_path).mkdir(exist_ok=True)

        # Write the metadata file
        with open(self._metadata_file, "w", encoding="utf-8") as metadataFile:
            self._metadata.write(metadataFile)

    def _validate(self) -> bool:
        """Check current metadata values.

        Returns
        -------

        is_valid: bool
           True if the metadata file is valid, False otherwise.
        """

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
