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
                 min_games: GamesRestriction,
                 last_notified: datetime,
                 team_pm_template: str):
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
        self.last_notified = last_notified
        self.team_pm_template = team_pm_template

    def describe(self) -> str:
        valid = self.is_valid()
        title = '[bold]{name}[/bold] [italic]{description}[/italic]'
        if not self.is_valid():
            title += ' [red bold]INVALID[/red bold]'
        title = title.format(name=self.name, description=f'({self.description})' if self.description else '')
        return '''{title}
    [red]{recurrence}[/red] [yellow]{variant}[/yellow] [blue]{time}[/blue]+[green]{increment}[/green]
    Next tournament: {date}'''.format(title=title,
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
            self.variant == existing.variant and
            self.team_restriction == existing.required_team
        )

    def is_valid(self, with_output: bool = False):
        # conditions from https://github.com/lichess-org/lila/blob/master/modules/tournament/src/main/TournamentForm.scala
        valid = True
        if self.clock_time.float_val() + self.clock_increment.int_val() == 0:
            if with_output: failure('[red bold]INVALID[/red bold] Clock time and increment must add to more than 0')
            valid = False
        if self.rated:
            allow_rated = self.variant == Variant.STANDARD or self.clock_time.float_val() > 0 or self.clock_increment.int_val() > 0
            if not allow_rated:
                if with_output: failure('[red bold]INVALID[/red bold] Rated games require standard variant or longer clock_time / clock_increment')
                valid = False
        estimated_game_seconds = (60 * self.clock_time.float_val() + 30 * self.clock_increment.int_val()) * 2 * 0.8 + 15
        estimated_number_of_games = (self.length_mins.int_val() * 60) / estimated_game_seconds
        if estimated_number_of_games < 3:
            if with_output: failure('[red bold]INVALID[/red bold] Increase tournament duration, or decrease game clock')
            valid = False
        if estimated_number_of_games > 150:
            if with_output: failure('[red bold]INVALID[/red bold] Reduce tournament duration, or increase game clock')
            valid = False
        return valid
        

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