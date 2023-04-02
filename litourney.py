import typer
import util.prompts as prompts
from models.config import Config

app = typer.Typer()

@app.command()
def setup(api_key: str = prompts.API_KEY, num_days: int = prompts.NUM_DAYS):
    """
    Setup config file
    """
    Config(api_key, num_days).save()

@app.command()
def refresh():
    """
    Refresh lichess information (teams you can access)
    """
    print("refresh")

@app.command()
def create():
    """
    Creates configured tournaments within the next X days (from config file)
    """
    print("create")

@app.command()
def new():
    """
    Configure a new recurring tournament
    """
    print("new")

@app.command()
def list():
    """
    Lists configured tournaments
    """
    print("list")

@app.command()
def delete(id: int):
    """
    Deletes a configured tournament
    """
    print("delete")

if __name__ == "__main__":
    app()