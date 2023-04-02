import typer
import util.config as config

app = typer.Typer()

@app.command()
def setup(api_key: str = typer.Option(..., prompt="Enter your Lichess API key"), num_days: int = typer.Option(..., prompt="How many days in the future should tournaments be created?")):
    """
    Setup config file
    """
    config.write(api_key, num_days)

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