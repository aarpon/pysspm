import typer

# Instantiate Typer
app = typer.Typer(name="project", help="Manage projects.")


@app.command("create")
def create(name: str, user_name: str, user_email: str, user_group: str):
    """Create a new project."""
    typer.echo(f"Create a new project with the passed arguments.")


@app.command("list")
def show():
    """List all projects."""
    typer.echo(f"List all projects.")
