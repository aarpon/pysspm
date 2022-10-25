import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pyspm import __version__
from pyspm.cli import CONFIG_PARSER, app
from pyspm.project import ProjectManager

# Instantiate a CliRunner object to be able to test the cli app
runner = CliRunner()


@pytest.fixture(autouse=False)
def run_before_and_after_tests(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    # First, make sure not to modify current config
    conf_file = Path(Path.home(), ".config/pyspm/pyspm.ini")
    restore_config = False
    bkp_conf_file = None
    if conf_file.is_file():
        bkp_conf_file = conf_file.parent / f"{conf_file.stem}_BACKUP.ini"
        shutil.copyfile(conf_file, bkp_conf_file)
        if bkp_conf_file.is_file():
            conf_file.unlink()
        restore_config = True

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # If needed, restore the original configuration file
    if restore_config and bkp_conf_file is not None:
        shutil.copyfile(bkp_conf_file, conf_file)
        bkp_conf_file.unlink()


def test_cli(run_before_and_after_tests):
    # Reset the configuration
    CONFIG_PARSER.reset()
    conf_file = Path(Path.home(), ".config/pyspm/pyspm.ini")
    assert conf_file.is_file()

    # Check the version
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output == f"Simple (scientific) Project Manager v{__version__}\n"

    # Get the projects.location config value: it should be empty
    result = runner.invoke(app, ["config", "get", "projects.location"])
    assert result.exit_code == 0
    assert result.output == "projects.location = \n"

    # Replace it with a new value and check that the new value is saved
    test_value = "/Users/aaron/Project"
    result = runner.invoke(app, ["config", "set", "projects.location", test_value])
    assert result.exit_code == 0

    result = runner.invoke(app, ["config", "get", "projects.location"])
    assert result.exit_code == 0
    new_value = re.search("projects.location = (.+?)\n", result.output).group(1)
    assert test_value == new_value

    # Create a couple of projects in a temporary directory
    with tempfile.TemporaryDirectory() as temp_project_dir:
        # Create and assign a temporary directory for tests
        result = runner.invoke(
            app, ["config", "set", "projects.location", temp_project_dir]
        )
        assert result.exit_code == 0

        # Check that there are no projects
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        print(result.output == "No projects found.\n")

        # Also check using the ProjectManager
        project_data_frame = ProjectManager.get_projects(
            CONFIG_PARSER["projects.location"]
        )
        assert project_data_frame is None

        # Add a project
        result = runner.invoke(
            app,
            [
                "project",
                "create",
                "--title",
                "Project A",
                "--user-name",
                "John Doe",
                "--user-email",
                "john.doe@example.com",
                "--user-group",
                "Group 1",
                "--short-descr",
                "",
                "--extern-git-repos",
                "",
            ],
        )
        assert result.exit_code == 0

        # Get the list of projects using the ProjectManager
        project_data_frame = ProjectManager.get_projects(
            CONFIG_PARSER["projects.location"]
        )
        assert len(project_data_frame.index) == 1

        # Add another project
        result = runner.invoke(
            app,
            [
                "project",
                "create",
                "--title",
                "Project B",
                "--user-name",
                "Jane Morris",
                "--user-email",
                "jane.morris@example.com",
                "--user-group",
                "Group 2",
                "--short-descr",
                "",
                "--extern-git-repos",
                "",
            ],
        )
        assert result.exit_code == 0

        # Get the list of projects using the ProjectManager
        project_data_frame = ProjectManager.get_projects(
            CONFIG_PARSER["projects.location"]
        )
        assert len(project_data_frame.index) == 2

        # Get some statistics
        result = runner.invoke(app, ["stats", "show"])
        assert result.exit_code == 0
        rows = result.stdout.split("\n")
        assert len(rows) == 8

        # Add collaborators with non-ASCII characters
        collaborator = "Jörg Müller"
        result = runner.invoke(app, ["project", "set", "P_0000", "user.collaborators", collaborator])
        assert result.exit_code == 0

        # Retrieve collaborator and check encoding
        result = runner.invoke(app, ["project", "get", "P_0000", "user.collaborators"])
        assert result.exit_code == 0
        ret_collaborator = result.output.rstrip()
        assert ret_collaborator == collaborator

        # Close project P_0000 "now"
        result = runner.invoke(app, ["project", "close", "P_0000", "now"])
        assert result.exit_code == 0

        # Close project P_0001 at "latest" modification
        result = runner.invoke(app, ["project", "close", "P_0001", "latest"])
        assert result.exit_code == 0
