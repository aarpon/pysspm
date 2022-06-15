import typer

from pyspm.config import ConfigurationManager

# Load configuration (singleton)
CONFIG_MANAGER = ConfigurationManager()


# Instantiate Typer
app = typer.Typer(name="config", help="Manage configuration options.")


@app.command("show")
def show():
    """Show current configuration options."""
    typer.echo(typer.style("Current configuration:", fg=typer.colors.GREEN, bold=True))
    for key in CONFIG_MANAGER.keys():
        typer.echo(f"{key} = {CONFIG_MANAGER[key]}")


@app.command("set")
def set(name: str, value: str):
    """Set the option with specified name to the passed value."""
    typer.echo("Set the option with specified name to the passed value.")


@app.command("get")
def get(key: str):
    """Get the value of the option with specified key."""
    try:
        typer.echo(f"{key} = {CONFIG_MANAGER[key]}")
    except ValueError as e:
        typer.echo(typer.style(f"Error: Configuration key '{key}' does not exist.", fg=typer.colors.RED, bold=True))
