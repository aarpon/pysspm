import typer

# Instantiate Typer
app = typer.Typer(name="stats", help="Collect statistics.")


@app.command("show")
def show(filter: str = ""):
    """Show all statistics, possibly filtered."""
    typer.echo(
        typer.style(
            "Sorry, this function has not yet been implemented.", fg=typer.colors.RED, bold=True
        )
    )
    raise typer.Exit()
