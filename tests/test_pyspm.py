from typer.testing import CliRunner

from pyspm import __version__
from pyspm.cli import app

# Instantiate a CliRunner object to be able to test the cli app
runner = CliRunner()


def test_version():
    assert __version__ == "0.1.0"


def test_app_init():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output == f"{__version__}\n"
