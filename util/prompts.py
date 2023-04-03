from datetime import datetime, timezone
from enum import StrEnum
from typing import List
import typer
from models.Tournament import Tournament
from models.UserInfo import load_user_info
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.ClockTime import ClockTime
from models.lichess.Variant import Variant
from util.funi import success

class AwfulTournamentEnum(StrEnum):
    name = 'name'
    clock_time = 'clock_time'
    clock_increment = 'clock_increment'
    length_mins = 'length_mins'
    recurrence = 'recurrence'
    first_date_utc = 'first_date_utc'
    variant = 'variant'
    rated = 'rated'
    positionFEN = 'positionFEN'
    berserkable = 'berserkable'
    streakable = 'streakable'
    has_chat = 'has_chat'
    description = 'description'
    team_restriction = 'team_restriction'
    min_rating = 'min_rating'
    max_rating = 'max_rating'
    min_games = 'min_games'
    cancel = 'exit'

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
    clock_time_seconds = clock_time.float_val() * 60
    if clock_increment.int_val() <= (clock_time_seconds * 2):
        return typer.prompt("Enable berserking?", type=bool)
    return False

def position_fen_prompt(variant: Variant):
    if variant == Variant.FROM_POSITION:
        return typer.prompt("Enter a custom initial position (in FEN) for all games of the tournament. Must be a legal chess position.\nFEN", type=str)
    return None

def team_restrictions_prompt(teams: List[str]):
    num_teams = len(teams)
    if num_teams == 0:
        success("You have no teams so the option to restrict tournament to a particular team is not shown")
        return None
    elif num_teams == 1:
        restrict = typer.prompt(f'Do you want to restrict the tourney to your team ({teams[0]})', type=bool)
        return teams[0] if restrict else None
    else:
        team_list = '\n'.join(f'    {i+1}: {team}' for (i,team) in enumerate(teams))
        message = f'Pick a team to restrict the tourney to:\n    0: Unrestricted\n{team_list}\nTeam'
        id = typer.prompt(message, type=int)
        return None if id == 0 else teams[id-1]

def edit_tournament_property_prompt(tournament: Tournament):
    type_mappings = {prop: type(tournament.__dict__[(prop)]) for prop in AwfulTournamentEnum if prop != 'exit'}
    prop = typer.prompt(f'Edit which property? (or exit)', type=AwfulTournamentEnum)
    if prop == 'exit':
        return False
    if prop == 'first_date_utc':
        start_date = typer.prompt('What is the first date and time the tournament should occur (in your local time)? e.g. 2020-12-24 23:59:59.\nDate and time', formats=["%Y-%m-%d %H:%M:%S"], type=datetime)
        utc_date = start_date.astimezone(timezone.utc)
        tournament.__dict__[prop] = utc_date
    elif prop == 'team_restriction':
        user = load_user_info()
        team_list = '\n'.join(f'    {i+1}: {team}' for (i,team) in enumerate(user.teams))
        message = f'Pick a team to restrict the tourney to:\n    0: Unrestricted\n{team_list}\nTeam'
        id = typer.prompt(message, type=int)
        team = None if id == 0 else user.teams[id-1]
        tournament.__dict__[prop] = team
    else:
        prop_type = type_mappings[prop]
        hint = ''
        if issubclass(prop_type, StrEnum):
            hint = f' ({", ".join([v for v in prop_type])})'
        value = typer.prompt(f'Set value{hint}', type=type_mappings[prop])
        tournament.__dict__[prop] = value
    return True
    