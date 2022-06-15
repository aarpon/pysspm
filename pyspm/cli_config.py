import typer

# Instantiate Typer
app = typer.Typer(name="config", help="Manage configuration options.")


@app.command("list")
def show():
    """List configuration options."""
    typer.echo("List configuration options.")


@app.command("set")
def set(name: str, value: str):
    """Set the option with specified name to the passed value."""
    typer.echo("Set the option with specified name to the passed value.")


@app.command("get")
def get(name: str):
    """Get the value of the option with specified name."""
    typer.echo("Get the value of the option with specified name.")
