from datetime import datetime
import json
import os
from typing import List

import typer
from models.RecurrenceType import RecurrenceType
from models.lichess.ClockTime import ClockTime
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.GamesRestriction import GamesRestriction
from models.lichess.RatingRestriction import RatingRestriction
from models.lichess.TournamentLength import TournamentLength
from models.lichess.Variant import Variant
import util.constants as constants
from util.funi import failure

class Tournament:
    def __init__(self,
                 name: str,
                 clock_time: ClockTime,
                 clock_increment: ClockIncrement,
                 length_mins: TournamentLength,
                 recurrence: RecurrenceType,
                 first_date_utc: datetime,
                 variant: Variant,
                 rated: bool,
                 positionFEN: str,
                 berserkable: bool,
                 streakable: bool,
                 has_chat: bool,
                 description: str,
                 team_restriction: str,
                 min_rating: RatingRestriction,
                 max_rating: RatingRestriction,
                 min_games: GamesRestriction):
        self.name = name
        self.clock_time = clock_time
        self.clock_increment = clock_increment
        self.length_mins = length_mins
        self.recurrence = recurrence
        self.first_date_utc = first_date_utc
        self.variant = variant
        self.rated = rated
        self.positionFEN = positionFEN
        self.berserkable = berserkable
        self.streakable = streakable
        self.has_chat = has_chat
        self.description = description
        self.team_restriction = team_restriction
        self.min_rating = min_rating
        self.max_rating = max_rating
        self.min_games = min_games

    def describe(self) -> str:
        return '''[bold]{name}[/bold]
    [red]{recurrence}[/red] [yellow]{variant}[/yellow] [blue]{time}+{increment}[/blue]
    Next tournament: {date}'''.format(name=self.name,
                                    recurrence=self.recurrence,
                                    time=self.clock_time.value,
                                    increment=self.clock_increment.value,
                                    variant=self.variant,
                                    date=self.get_next_date().strftime("%Y-%m-%d %H:%M:%S"))

    def get_next_date(self) -> datetime:
        #TODO implement this
        return datetime.now()

def tournament_json_serializer(obj):
    if isinstance(obj, Tournament):
        return obj.__dict__
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def tournament_json_decoder(data):
    enum_mappings = {
        'clock_time': ClockTime,
        'clock_increment': ClockIncrement,
        'length_mins': TournamentLength,
        'recurrence': RecurrenceType,
        'variant': Variant,
        'min_rating': RatingRestriction,
        'max_rating': RatingRestriction,
        'min_games': GamesRestriction
    }
    for (key, type) in enum_mappings.items():
        data[key] = type(data[key])
    data['first_date_utc'] = datetime.fromisoformat(data['first_date_utc'])
    return Tournament(**data)

def save_tournaments(tourneys: List[Tournament]):
    with open(constants.TOURNAMENTS_FILENAME, 'w') as tourneysFile:
        tourneysFile.write(json.dumps(tourneys, default=tournament_json_serializer))

def load_tournaments() -> List[Tournament]:
    try:
        if not os.path.exists(constants.TOURNAMENTS_FILENAME):
            return []
        with open(constants.TOURNAMENTS_FILENAME, 'r') as tourneysFile:
            return json.loads(tourneysFile.read(), object_hook=tournament_json_decoder)
    except:
        failure('Failed to read tournaments file')
        if os.path.exists(constants.TOURNAMENTS_FILENAME):
            do_reset = typer.prompt("Do you want to delete the tournaments file and start again?", type=bool)
            if (do_reset): os.remove(constants.TOURNAMENTS_FILENAME)
        quit()