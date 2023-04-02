from typing import List
import typer
from util.funi import success

# Config
API_KEY = typer.Option(..., prompt="Enter your Lichess API key")
NUM_DAYS =  typer.Option(..., prompt="How many days in the future should tournaments be created?")

# Tournament
TOURNEY_NAME = typer.Option("", prompt="What name should be used for the tournament? Leave empty to get a random Grandmaster name")
CLOCK_TIME = typer.Option(..., prompt="Enter clock initial time in minutes")
CLOCK_INCREMENT = typer.Option(..., prompt="Enter clock increment in seconds")
TOURNEY_LENGTH = typer.Option(..., prompt="How long should the tournament last, in minutes?")
RECURRENCE_TYPE = typer.Option(..., prompt="How often should the tournament repeat?")
START_DATE_TIME = typer.Option(..., formats=["%Y-%m-%d %H:%M:%S"], prompt="What is the first date and time the tournament should occur (in your local time)? e.g. 2020-12-24 23:59:59.\nDate and time")
VARIANT = typer.Option(..., prompt="Which chess variant should the tournament be played in?")
RATED = typer.Option(..., prompt="Should the games be rated?")
POSITION_FEN = typer.Option(..., prompt="Enter a custom initial position (in FEN) for all games of the tournament. Must be a legal chess position.")
BERSERKABLE = typer.Option(..., prompt="Should the players be able to use berserk?")
STREAKABLE = typer.Option(..., prompt="Should streaks be enabled? (After 2 wins, consecutive wins grant 4 points instead of 2)")
HAS_CHAT = typer.Option(..., prompt="Should chat be enabled?")
DESCRIPTION = typer.Option('', prompt="Enter a description of the tournament (optional)")
MIN_RATING = typer.Option(..., prompt="Enter a minimum rating to join, or leave empty to let everyone join")
MAX_RATING = typer.Option(..., prompt="Enter a maximum rating to join, or leave empty to let everyone join")
MIN_GAMES = typer.Option(..., prompt="Enter a minimum number of rated games to join, or leave empty to let everyone join")

def team_restrictions_prompt(my_teams: List[str]):
    num_teams = len(my_teams)
    if num_teams == 0:
        success("You have no teams so the option to restrict tournament to a particular team is not shown")
        return None
    elif num_teams == 1:
        restrict: bool = typer.prompt(f'Do you want to restrict the tourney to your team ({my_teams[0]})', type=bool)
        return my_teams[0] if restrict else None
    else:
        team_list = '\n'.join(f'    {i+1}: {team}' for (i,team) in enumerate(my_teams))
        message = f'Pick a team to restrict the tourney to:\n    0: Unrestricted\n{team_list}\nTeam'
        id: int = typer.prompt(message, type=int)
        return None if id == 0 else my_teams[id-1]