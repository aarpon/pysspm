import typer

from pysspm.cli_init import check_if_initialized
from pysspm.config import ConfigurationParser

# Load configuration (singleton)
CONFIG_PARSER = ConfigurationParser()


# Instantiate Typer
app = typer.Typer(name="config", help="Manage configuration options.")


@app.command("location")
def location():
    """Show full path of configuration file."""

    # Make sure sspm configuration is initialized
    check_if_initialized()

    # Report full path to configuration file
    typer.echo(typer.style(f"Configuration file: {CONFIG_PARSER.config_file}"))


@app.command("show")
def show():
    """Show current configuration options."""

    # Make sure sspm configuration is initialized
    check_if_initialized()

    typer.echo(typer.style("Current configuration:", fg=typer.colors.GREEN, bold=True))
    for key in CONFIG_PARSER.keys():
        typer.echo(f"{key} = {CONFIG_PARSER[key]}")

    typer.echo("")
    typer.echo(
        typer.style(
            "Use `sspm config set <key> <value>` to change configuration.\n"
            + "Use `sspm config keys` to show the list of valid config keys.",
            fg=typer.colors.GREEN,
            bold=True,
        )
    )


@app.command("set")
def set(item: str, value: str):
    """Set the option with specified name to the passed value."""

    try:
        CONFIG_PARSER[item] = value
    except ValueError as e:
        typer.echo(
            typer.style(
                f"Error: Configuration key '{item}' does not exist.",
                fg=typer.colors.RED,
                bold=True,
            )
        )


@app.command("get")
def get(key: str):
    """Get the value of the option with specified key."""

    try:
        typer.echo(f"{key} = {CONFIG_PARSER[key]}")
    except ValueError as e:
        typer.echo(
            typer.style(
                f"Error: Configuration key '{key}' does not exist.",
                fg=typer.colors.RED,
                bold=True,
            )
        )


@app.command("keys")
def keys():
    """Show the list of valid configuration keys."""
    typer.echo(f"Valid configuration keys are: {CONFIG_PARSER.valid_keys}.")
