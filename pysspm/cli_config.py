import typer

from pysspm.config import ConfigurationParser

# Load configuration (singleton)
CONFIG_PARSER = ConfigurationParser()


# Instantiate Typer
app = typer.Typer(name="config", help="Manage configuration options.")


@app.command("location")
def location():
    """Show full path of configuration file."""
    if not CONFIG_PARSER.is_valid:
        typer.echo(
            typer.style(
                "Error: sspm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
    else:
        typer.echo(typer.style(f"Configuration file: {CONFIG_PARSER.config_file}"))


@app.command("show")
def show():
    """Show current configuration options."""
    if not CONFIG_PARSER.is_valid:
        typer.echo(
            typer.style(
                "Error: sspm is not configured yet.", fg=typer.colors.RED, bold=True
            )
        )
    typer.echo(typer.style("Current configuration:", fg=typer.colors.GREEN, bold=True))
    for key in CONFIG_PARSER.keys():
        typer.echo(f"{key} = {CONFIG_PARSER[key]}")


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
    typer.echo(f"Valid configuration keys are : {CONFIG_PARSER.valid_keys}.")
