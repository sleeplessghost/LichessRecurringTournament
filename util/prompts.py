from datetime import datetime, timezone
from enum import StrEnum
from typing import List
import typer
from models.Templating import NameReplacement, TemplateReplacement
from models.Tournament import Tournament
from models.TournamentType import TournamentType
from models.UserInfo import load_user_info
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.ClockTime import ClockTime
from models.lichess.Variant import Variant
from util.funi import failure, success

class AwfulTournamentEnum(StrEnum):
    type = 'type'
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
    min_games = 'min_games',
    team_pm_template = 'team_pm_template',
    last_id = 'last_id'
    num_leaders = 'num_leaders'
    cancel = 'exit'

# Config
API_KEY = typer.Option(..., prompt="Enter your Lichess API personal access token")
NUM_DAYS =  typer.Option(..., prompt="How many days in the future should tournaments be created?")

# Tournament
TOURNEY_TYPE = typer.Option(..., prompt="Tournament type?")
TOURNEY_NAME = typer.Option("", prompt=f"Tournament name? Leave empty to get a random Grandmaster name.\nYou can also include {NameReplacement.WINNER.value} and it will be replaced with the previous tournament winner's name.\nShould not be longer than 30 characters")
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

def team_battle_teams_prompt(teams: List[str]):
    num_teams = len(teams)
    if num_teams <= 1:
        failure(f'You have {num_teams} team(s) so you cannot create a team battle')
    else:
        team_list = '\n'.join(f'    {i+1}: {team}' for (i,team) in enumerate(teams))
        message = f'Pick which teams to restrict the tourney to (enter their numbers separated by commas):\n{team_list}\nTeams'
        ids_str = typer.prompt(message, type=str)
        return [teams[int(id) - 1] for id in ids_str.split(',')]

def num_leaders_prompt(type: TournamentType):
    if type == TournamentType.TeamBattle:
        return typer.prompt('How many leaders should each team have?', type=int)
    return 0

def team_pm_template_prompt(team_id: str):
    if team_id is None:
        return ''
    prompt_msg = f"""Do you want to send a 24 hour pre-tournament PM reminder to the team? If so, enter a template to be used for the PM.
Special values which will be automatically replaced (including square brackets):
    {TemplateReplacement.NAME.value} : Tournament name
    {TemplateReplacement.VARIANT.value} : Variant used for the tournament
    {TemplateReplacement.CLOCKTIME.value} : Initial clock time
    {TemplateReplacement.INCREMENT.value} : Clock increment
    {TemplateReplacement.LINK.value} : Link to the tournament
    {TemplateReplacement.BREAK.value} : Line break
    [timezone:Europe/London] : Show the start date/time for the tournament in the specified timezone https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
If you don't want to send a PM reminder, you can leave this blank.
Template"""
    return typer.prompt(prompt_msg, type=str, default="", show_choices=False)

def edit_tournament_property_prompt(tournament: Tournament):
    # awful
    type_mappings = {prop: type(tournament.__dict__[(prop)]) for prop in AwfulTournamentEnum if prop != 'exit'}
    prop = typer.prompt(f'Edit which property? (or exit)', type=AwfulTournamentEnum)
    if prop == 'exit':
        return False
    if prop == 'first_date_utc':
        start_date = typer.prompt('What is the first date and time the tournament should occur (in your local time)? e.g. 2020-12-24 23:59:59.\nDate and time', type=datetime, value_proc=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
        utc_date = start_date.astimezone(timezone.utc)
        tournament.__dict__[prop] = utc_date
    elif prop == 'team_restriction' and tournament.type != TournamentType.TeamBattle:
        user = load_user_info()
        team_list = '\n'.join(f'    {i+1}: {team}' for (i,team) in enumerate(user.teams))
        message = f'Pick a team to restrict the tourney to:\n    0: Unrestricted\n{team_list}\nTeam'
        id = typer.prompt(message, type=int)
        team = None if id == 0 else user.teams[id-1]
        tournament.__dict__[prop] = team
    elif prop == 'team_restriction' and tournament.type == TournamentType.TeamBattle:
        user = load_user_info()
        team_list = '\n'.join(f'    {i+1}: {team}' for (i,team) in enumerate(user.teams))
        message = f'Pick which teams to restrict the tourney to (enter their numbers separated by commas):\n{team_list}\nTeams'
        ids_str = typer.prompt(message, type=str)
        teams = [user.teams[int(id) - 1] for id in ids_str.split(',')]
        tournament.__dict__[prop] = ','.join(teams)
    else:
        prop_type = type_mappings[prop]
        hint = ''
        default = None
        if issubclass(prop_type, StrEnum):
            hint = f' ({", ".join([v for v in prop_type])})'
        if prop_type is str:
            default = ''
        value = typer.prompt(f'Set value{hint}', type=type_mappings[prop], default=default)
        tournament.__dict__[prop] = value
    return True
    