from datetime import datetime
import typer
from models.RecurrenceType import RecurrenceType
from models.Tournament import Tournament
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.ClockTime import ClockTime
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
        recurrence: RecurrenceType = prompts.RECURRENCE_TYPE,
        start_date_time: datetime = prompts.START_DATE_TIME,
        clock_time: ClockTime = prompts.CLOCK_TIME,
        clock_increment: ClockIncrement = prompts.CLOCK_INCREMENT,
        tournament_length: TournamentLength = prompts.TOURNEY_LENGTH,
        variant: Variant = prompts.VARIANT,
        rated: bool = prompts.RATED,
        has_chat: bool = prompts.HAS_CHAT,
        description: str = prompts.DESCRIPTION,
        min_rating: RatingRestriction = prompts.MIN_RATING,
        max_rating: RatingRestriction = prompts.MAX_RATING,
        min_games: RatingRestriction = prompts.MAX_RATING,
        streakable: bool = prompts.STREAKABLE):
    """
    Configure a new recurring tournament
    """
    clock_time_seconds = int(clock_time) * 60
    berserkable = False
    if int(clock_increment) <= (clock_time_seconds * 2):
        berserkable = prompts.BERSERKABLE
    position_FEN = None
    if variant == Variant.FROM_POSITION:
        position_FEN = prompts.POSITION_FEN
    #TODO get actual teams
    team_restriction = prompts.team_restrictions_prompt(['my', 'teams'])
    #TODO handle date properly
    date_utc = datetime.now()
    tournament = Tournament(name, clock_time, clock_increment, tournament_length, recurrence, date_utc,
                            variant, rated, position_FEN, berserkable, streakable, has_chat, description,
                            team_restriction, min_rating, max_rating, min_games)

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