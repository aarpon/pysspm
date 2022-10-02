import re

from typer.testing import CliRunner

from pyspm import __version__
from pyspm.cli import app, CONFIG_PARSER
from pyspm.project import ProjectManager

# Instantiate a CliRunner object to be able to test the cli app
runner = CliRunner()


def test_version():
    assert __version__ == "0.1.0"


def test_app_init():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output == f"Simple (scientific) Project Manager v{__version__}\n"


def test_set_config_value():
    # Retrieve current value
    result = runner.invoke(app, ["config", "get", "projects.location"])
    assert result.exit_code == 0
    current_value = re.search("projects.location = (.+?)\n", result.output).group(1)

    # Replace it with a new value and check that the new value is saved
    test_value = "/Users/aaron/Project"
    result = runner.invoke(app, ["config", "set", "projects.location", test_value])
    assert result.exit_code == 0

    result = runner.invoke(app, ["config", "get", "projects.location"])
    assert result.exit_code == 0
    new_value = re.search("projects.location = (.+?)\n", result.output).group(1)
    assert test_value == new_value

    # Restore original value
    result = runner.invoke(app, ["config", "set", "projects.location", current_value])
    assert result.exit_code == 0


def test_get_project_list():
    # Retrieve the projects table
    project_data, headers = ProjectManager.get_projects(
        CONFIG_PARSER["projects.location"], None
    )
    assert len(project_data) > 0
