from datetime import datetime, timezone
import json
from typing import List
import typer
from models.RecurrenceType import RecurrenceType
from models.Tournament import Tournament, load_tournaments, save_tournaments, tournament_json_serializer
from models.UserInfo import load_user_info
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.ClockTime import ClockTime
from models.lichess.GamesRestriction import GamesRestriction
from models.lichess.RatingRestriction import RatingRestriction
from models.lichess.TournamentLength import TournamentLength
from models.lichess.Variant import Variant
import util.prompts as prompts
from models.Config import Config
from util.funi import success
from rich import print

app = typer.Typer()

@app.command()
def setup(api_key: str = prompts.API_KEY, num_days: int = prompts.NUM_DAYS):
    """
    Setup config file
    """
    Config(api_key, num_days).save()
    success()

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
def new(name: str = prompts.TOURNEY_NAME,
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
    team_restriction = prompts.team_restrictions_prompt(user_info)
    date_utc = start_date_time.astimezone(timezone.utc)
    tournament = Tournament(name, clock_time, clock_increment, tournament_length, recurrence, date_utc,
                            variant, rated, position_FEN, berserkable, streakable, has_chat, description,
                            team_restriction, min_rating, max_rating, min_games)
    existing = load_tournaments()
    existing.append(tournament)
    save_tournaments(existing)
    success()

@app.command()
def list():
    """
    Lists configured tournaments
    """
    tourneys = load_tournaments()
    print_tourneys(tourneys)

@app.command()
def delete(delete_all: bool = False):
    """
    Deletes a configured tournament
    """
    if delete_all:
        save_tournaments([])
    else:
        tourneys = load_tournaments()
        print_tourneys(tourneys)
        id = typer.prompt('Which tournament should be deleted? Or 0 to cancel', type=int)
        if id > 0:
            del tourneys[id-1]
            save_tournaments(tourneys)
    success()
    
def print_tourneys(tourneys: List[Tournament]):
    mapped = [tourney.describe() for tourney in tourneys]
    for (i, desc) in enumerate(mapped):
        print(f'{i+1}:  {desc}')

if __name__ == "__main__":
    app()