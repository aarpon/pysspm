import typer

# Instantiate Typer
app = typer.Typer(name="stats", help="Collect statistics.")


@app.command("show")
def show(filter: str = ""):
    """Show all statistics, possibly filtered."""
    typer.echo(f"Show all statistics, possibly filtered.")
