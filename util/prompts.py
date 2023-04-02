import typer

API_KEY = typer.Option(..., prompt="Enter your Lichess API key")
NUM_DAYS =  typer.Option(..., prompt="How many days in the future should tournaments be created?")