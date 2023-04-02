from datetime import datetime
import json
import typer
from models.RecurrenceType import RecurrenceType
from models.Tournament import Tournament, load_tournaments, save_tournaments
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.ClockTime import ClockTime
from models.lichess.GamesRestriction import GamesRestriction
from models.lichess.RatingRestriction import RatingRestriction
from models.lichess.TournamentLength import TournamentLength
from models.lichess.Variant import Variant
import util.prompts as prompts
from models.Config import Config
from util.funi import success

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
    #TODO get actual teams
    team_restriction = prompts.team_restrictions_prompt(['my', 'teams'])
    #TODO handle date properly
    date_utc = datetime.now()
    tournament = Tournament(name, clock_time, clock_increment, tournament_length, recurrence, date_utc,
                            variant, rated, position_FEN, berserkable, streakable, has_chat, description,
                            team_restriction, min_rating, max_rating, min_games)
    existing = load_tournaments()
    existing.append(tournament)
    save_tournaments(existing)

@app.command()
def list():
    """
    Lists configured tournaments
    """
    print(list)

@app.command()
def delete(id: int):
    """
    Deletes a configured tournament
    """
    print("delete")

if __name__ == "__main__":
    app()