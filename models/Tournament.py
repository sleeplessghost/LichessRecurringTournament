from datetime import datetime, timedelta, timezone
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
from models.lichess.TournamentResponse import TournamentResponse
from models.lichess.Variant import Variant
import util.constants as constants
from util.funi import failure, success

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
        return '''[bold]{name}[/bold] [italic]{description}[/italic]
    [red]{recurrence}[/red] [yellow]{variant}[/yellow] [blue]{time}[/blue]+[green]{increment}[/green]
    Next tournament: {date}'''.format(name=self.name,
                                    description=f'({self.description})' if self.description else '',
                                    recurrence=self.recurrence,
                                    time=self.clock_time.value,
                                    increment=self.clock_increment.value,
                                    variant=self.variant,
                                    date=self.get_next_date().strftime("%Y-%m-%d %H:%M:%S"))

    def get_next_date(self) -> datetime:
        utc_now = datetime.now().astimezone(timezone.utc)
        if self.first_date_utc >= utc_now:
            return self.first_date_utc
        next_date = datetime(utc_now.year, utc_now.month, utc_now.day, self.first_date_utc.hour, self.first_date_utc.minute, self.first_date_utc.second, tzinfo=timezone.utc)
        if self.recurrence == RecurrenceType.DAILY:
            if next_date < utc_now:
                next_date += timedelta(days=1)
        elif self.recurrence == RecurrenceType.WEEKLY or self.recurrence == RecurrenceType.FORTNIGHTLY:
            original_weekday = self.first_date_utc.weekday()
            next_weekday = next_date.weekday()
            if next_date < utc_now or next_weekday != original_weekday:
                days = (original_weekday - next_weekday) % 7
                next_date += timedelta(days=days)
            if self.recurrence == RecurrenceType.FORTNIGHTLY:
                weeks_between = (next_date - self.first_date_utc).days // 7
                if weeks_between % 2 != 0:
                    next_date += timedelta(days=7)
        elif self.recurrence == RecurrenceType.MONTHLY:
            if next_date < utc_now or next_date.day != self.first_date_utc.day:
                next_date = datetime(utc_now.year, utc_now.month + 1, self.first_date_utc.day, self.first_date_utc.hour, self.first_date_utc.minute, self.first_date_utc.second, tzinfo=timezone.utc)
        else:
            raise Warning(f'unhandled Recurrence type: {self.recurrence}')
        return next_date

    def has_restrictions(self) -> bool:
        return self.team_restriction is not None or self.min_rating != RatingRestriction.NONE or self.max_rating != RatingRestriction.NONE or self.min_games != GamesRestriction.NONE

    def already_created(self, created: List[TournamentResponse]) -> bool:
        return any(self.matches(t) for t in created)

    def matches(self, existing: TournamentResponse) -> bool:
        return (
            (self.name == '' or self.name == existing.name) and
            self.rated == existing.rated and
            self.clock_increment.int_val() == existing.clock_increment and
            int(self.get_next_date().timestamp() * 1000) == existing.starts_at_ms and
            self.variant == existing.variant
        )

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
            success()
        quit()