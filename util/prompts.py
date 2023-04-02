from typing import List
import typer
from models.UserInfo import UserInfo
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.ClockTime import ClockTime
from models.lichess.Variant import Variant
from util.funi import success

# Config
API_KEY = typer.Option(..., prompt="Enter your Lichess API key")
NUM_DAYS =  typer.Option(..., prompt="How many days in the future should tournaments be created?")

# Tournament
TOURNEY_NAME = typer.Option("", prompt="Tournament name? Leave empty to get a random Grandmaster name")
CLOCK_TIME = typer.Option(..., prompt="Initial clock time (in minutes)?")
CLOCK_INCREMENT = typer.Option(..., prompt="Clock increment (in seconds)?")
TOURNEY_LENGTH = typer.Option(..., prompt="Tournament length (in minutes)?")
RECURRENCE_TYPE = typer.Option(..., prompt="How often should the tournament repeat?")
START_DATE_TIME = typer.Option(..., formats=["%Y-%m-%d %H:%M:%S"], prompt="What is the first date and time the tournament should occur (in your local time)? e.g. 2020-12-24 23:59:59.\nDate and time")
VARIANT = typer.Option(..., prompt="Chess variant?")
RATED = typer.Option(..., prompt="Rated games?")
STREAKABLE = typer.Option(..., prompt="Enable streaks? (After 2 wins, consecutive wins grant 4 points instead of 2)")
HAS_CHAT = typer.Option(..., prompt="Enable chat?")
DESCRIPTION = typer.Option("", prompt="Tournament description (optional)")
MIN_RATING = typer.Option(..., prompt="Required minimum rating?")
MAX_RATING = typer.Option(..., prompt="Required maximum rating?")
MIN_GAMES = typer.Option(..., prompt="Required minimum rated games played?")

def berserkable_prompt(clock_time: ClockTime, clock_increment: ClockIncrement):
    clock_time_seconds = clock_time.int_val() * 60
    if clock_increment.int_val() <= (clock_time_seconds * 2):
        return typer.prompt("Enable berserking?", type=bool)
    return False

def position_fen_prompt(variant: Variant):
    if variant == Variant.FROM_POSITION:
        return typer.prompt("Enter a custom initial position (in FEN) for all games of the tournament. Must be a legal chess position.\nFEN", type=str)
    return None

def team_restrictions_prompt(user_info: UserInfo):
    num_teams = len(user_info.teams)
    if num_teams == 0:
        success("You have no teams so the option to restrict tournament to a particular team is not shown")
        return None
    elif num_teams == 1:
        restrict = typer.prompt(f'Do you want to restrict the tourney to your team ({user_info.teams[0]})', type=bool)
        return user_info.teams[0] if restrict else None
    else:
        team_list = '\n'.join(f'    {i+1}: {team}' for (i,team) in enumerate(user_info.teams))
        message = f'Pick a team to restrict the tourney to:\n    0: Unrestricted\n{team_list}\nTeam'
        id = typer.prompt(message, type=int)
        return None if id == 0 else user_info.teams[id-1]