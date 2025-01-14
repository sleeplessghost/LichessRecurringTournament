from datetime import datetime, timezone
from typing import List
import typer
from models.RecurrenceType import RecurrenceType
from models.Tournament import Tournament, load_tournaments, save_tournaments
from models.TournamentType import TournamentType
from models.UserInfo import UserInfo, load_user_info
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.ClockTime import ClockTime
from models.lichess.GamesRestriction import GamesRestriction
from models.lichess.RatingRestriction import RatingRestriction
from models.lichess.TournamentLength import TournamentLength
from models.lichess.Variant import Variant
import util.prompts as prompts
from models.config import Config, load_config
from util.funi import success
from rich import print
from rich.markup import escape
import util.lichess_api as lichess

app = typer.Typer()

@app.command()
def setup(api_key: str = prompts.API_KEY, num_days: int = prompts.NUM_DAYS):
    """
    Setup config file
    """
    Config(api_key, num_days).save()
    success('configured')

@app.command()
def refresh():
    """
    Refresh lichess information (your username and teams you lead)
    """
    config = load_config()
    username = lichess.username(config.api_key)
    teams = lichess.teams(config.api_key, username)
    user = UserInfo(username, teams)
    user.save()
    success(f'username: {user.username}, teams: {user.teams}')

@app.command()
def create():
    """
    Creates configured tournaments within the next X days (from config file)
    """
    config = load_config()
    user = load_user_info()
    tourneys = load_tournaments()
    existing = lichess.my_tournaments(config.api_key, user.username)
    to_create = [t for t in tourneys if t.is_valid() and not t.already_created(existing)]
    to_create = [t for t in to_create if (t.get_next_date() - datetime.now(timezone.utc)).days <= config.num_days]
    if len(to_create) == 0:
        success('nothing to create')
    else:
        for tourney in to_create:
            created = lichess.create_tournament(config.api_key, tourney)
            tourney.last_id = created.id
            save_tournaments(tourneys)
            success(f'{created.full_name} created')

@app.command()
def notify():
    """
    Sends out PMs to teams with tournaments starting in the next 24 hours (requires team and PM template to be set for the tournament)
    """
    config = load_config()
    user = load_user_info()
    tourneys = load_tournaments()
    existing = lichess.my_tournaments(config.api_key, user.username)
    to_notify = [t for t in tourneys if t.needs_notification() and t.already_created(existing)]
    if len(to_notify) == 0:
        success('nothing to notify')
    else:
        utc_now = datetime.now(timezone.utc)
        for tourney in to_notify:
            tourney_match = next(t for t in existing if tourney.matches(t))
            message = tourney.get_pm_message(tourney_match)
            if message:
                lichess.pm_team(config.api_key, tourney.team_restriction, message)
                tourney.last_notified = utc_now
                save_tournaments(tourneys)
                success(f'{tourney.team_restriction} notified for {tourney_match.full_name}')

@app.command()
def new(type: TournamentType = prompts.TOURNEY_TYPE,
        name: str = prompts.TOURNEY_NAME,
        description: str = prompts.DESCRIPTION,
        recurrence: RecurrenceType = prompts.RECURRENCE_TYPE,
        start_date_time: datetime = prompts.START_DATE_TIME,
        variant: Variant = prompts.VARIANT,
        clock_time: ClockTime = prompts.CLOCK_TIME,
        clock_increment: ClockIncrement = prompts.CLOCK_INCREMENT,
        tournament_length: TournamentLength = prompts.TOURNEY_LENGTH,
        min_rating: RatingRestriction = prompts.MIN_RATING,
        max_rating: RatingRestriction = prompts.MAX_RATING,
        min_games: GamesRestriction = prompts.MIN_GAMES,
        rated: bool = prompts.RATED,
        has_chat: bool = prompts.HAS_CHAT,
        streakable: bool = prompts.STREAKABLE):
    """
    Configure a new recurring tournament
    """
    berserkable = prompts.berserkable_prompt(clock_time, clock_increment)
    position_FEN = prompts.position_fen_prompt(variant)
    user_info = load_user_info()
    team_restriction = None
    num_leaders = 0
    if type == TournamentType.TeamBattle:
        team_restriction = ','.join(prompts.team_battle_teams_prompt(user_info.teams))
        num_leaders = prompts.num_leaders_prompt(type)
    else:
        team_restriction = prompts.team_restrictions_prompt(user_info.teams)
    pm_template = '' if team_restriction is None else prompts.team_pm_template_prompt(team_restriction)
    date_utc = start_date_time.astimezone(timezone.utc)
    last_notified = None
    last_id = None
    tournament = Tournament(type, name, clock_time, clock_increment, tournament_length, recurrence, date_utc,
                            variant, rated, position_FEN, berserkable, streakable, has_chat, description,
                            team_restriction, min_rating, max_rating, min_games, pm_template, last_notified, last_id, num_leaders)
    existing = load_tournaments()
    existing.append(tournament)
    save_tournaments(existing)
    success(f'{tournament.name} saved')
    tournament.is_valid(with_output=True)

@app.command()
def edit():
    """
    Edit a configured tournament
    """
    tourneys = load_tournaments()
    print_tourneys(tourneys)
    id = typer.prompt('Which tournament should be edited? Or 0 to cancel', type=int)
    if id > 0:
        tourney = tourneys[id-1]
        editing = True
        while editing:
            print()
            for attribute,value in tourney.__dict__.items():
                print(escape(f'{attribute} = {value}'))
            tourney.is_valid(with_output=True)
            editing = prompts.edit_tournament_property_prompt(tourney)
            save_tournaments(tourneys)
            success()

@app.command()
def list():
    """
    Lists configured tournaments
    """
    tourneys = load_tournaments()
    print_tourneys(tourneys)

@app.command()
def delete(all: bool = False, invalid: bool = False):
    """
    Deletes a configured tournament (only the saved configuration, to cancel tournaments go on https://lichess.org)
    """
    if all:
        save_tournaments([])
        success('all gone')
    elif invalid:
        tourneys = load_tournaments()
        valid = [t for t in tourneys if t.is_valid()]
        save_tournaments(valid)
        success('invalids removed')
    else:
        tourneys = load_tournaments()
        print_tourneys(tourneys)
        id = typer.prompt('Which tournament should be deleted? Or 0 to cancel', type=int)
        tournament = None
        if id > 0:
            tournament = tourneys[id-1]
            del tourneys[id-1]
            save_tournaments(tourneys)
        message = '' if tournament is None else f'{tournament.name} deleted'
        success(message)

def print_tourneys(tourneys: List[Tournament]):
    if len(tourneys) == 0:
        success('there are no saved tournaments')
        quit()
    else:
        mapped = [tourney.describe() for tourney in tourneys]
        for (i, desc) in enumerate(mapped):
            print(f'{i+1}:  {desc}')

if __name__ == "__main__":
    app()