from datetime import datetime, timedelta, timezone
import json
import os
import re
from typing import List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import typer
from models.Templating import NameReplacement, TemplateReplacement
from models.RecurrenceType import RecurrenceType
from models.TournamentType import TournamentType
from models.lichess.ClockTime import ClockTime
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.GamesRestriction import GamesRestriction
from models.lichess.RatingRestriction import RatingRestriction
from models.lichess.TournamentLength import TournamentLength
from models.lichess.TournamentResponse import TournamentResponse
from models.lichess.Variant import Variant
import util.constants as constants
from util.funi import failure, success
from rich.markup import escape

class Tournament:
    def __init__(self,
                 type: TournamentType,
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
                 team_pm_template: str,
                 last_notified: datetime,
                 last_id: str,
                 num_leaders: int):
        self.type = type
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
        self.team_pm_template = team_pm_template
        self.last_notified = last_notified
        self.last_id = last_id
        self.num_leaders = num_leaders

    def describe(self) -> str:
        title = '[bold]{name}[/bold] ({type}) [italic]{description}[/italic]'
        if not self.is_valid():
            title += ' [red bold]INVALID[/red bold]'
        title = title.format(name=escape(self.name), type=self.type.value, description=f'({self.description})' if self.description else '')
        local_timezone = datetime.now().tzinfo
        return '''{title}
    [red]{recurrence}[/red] [yellow]{variant}[/yellow] [blue]{time}[/blue]+[green]{increment}[/green]
    Next tournament: {date}'''.format(title=title,
                                    recurrence=self.recurrence,
                                    time=self.clock_time.value,
                                    increment=self.clock_increment.value,
                                    variant=self.variant,
                                    date=self.get_next_date().astimezone(local_timezone))

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
            if next_weekday != original_weekday:
                days = (original_weekday - next_weekday) % 7
                next_date += timedelta(days=days)
            if next_date < utc_now:
                next_date += timedelta(days=7)
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
        return (self.team_restriction is not None and self.type != TournamentType.TeamBattle) or self.min_rating != RatingRestriction.NONE or self.max_rating != RatingRestriction.NONE or self.min_games != GamesRestriction.NONE

    def already_created(self, created: List[TournamentResponse]) -> bool:
        return any(self.matches(t) for t in created)

    def matches(self, existing: TournamentResponse) -> bool:
        return self.last_id == existing.id

    def is_valid(self, with_output: bool = False):
        # conditions from https://github.com/lichess-org/lila/blob/master/modules/tournament/src/main/TournamentForm.scala
        valid = True
        if self.name and len(self.name) > 30:
            if with_output: failure('[red bold]INVALID[/red bold] Name should be 30 characters or less')
            valid = False
        name_without_winner = self.name.replace(NameReplacement.WINNER.value, '')
        if any(c != ' ' and not c.isalnum() for c in name_without_winner):
            if with_output: failure('[red bold]INVALID[/red bold] Name should only have spaces or alphanumeric characters')
            valid = False
        if self.clock_time.float_val() + self.clock_increment.int_val() == 0:
            if with_output: failure('[red bold]INVALID[/red bold] Clock time and increment must add to more than 0')
            valid = False
        if self.rated:
            allow_rated = self.variant == Variant.STANDARD or self.clock_time.float_val() > 0 or self.clock_increment.int_val() > 1
            if not allow_rated:
                if with_output: failure('[red bold]INVALID[/red bold] Rated games require standard variant or longer clock_time / clock_increment')
                valid = False
        if self.berserkable:
            clock_time_seconds = self.clock_time.float_val() * 60
            if self.clock_increment.int_val() > (clock_time_seconds * 2):
                if with_output: failure('[red bold]INVALID[/red bold] Berserkable requires increment to be <= 2 * clock time (in seconds)')
                valid = False
        if self.min_rating != RatingRestriction.NONE and self.max_rating != RatingRestriction.NONE:
            if self.min_rating.int_val() >= self.max_rating.int_val():
                if with_output: failure('[red bold]INVALID[/red bold] Min rating should be less than max rating')
                valid = False
        estimated_game_seconds = (60 * self.clock_time.float_val() + 30 * self.clock_increment.int_val()) * 2 * 0.8 + 15
        estimated_number_of_games = (self.length_mins.int_val() * 60) / estimated_game_seconds
        if estimated_number_of_games < 3:
            if with_output: failure('[red bold]INVALID[/red bold] Increase tournament duration, or decrease game clock')
            valid = False
        if estimated_number_of_games > 150:
            if with_output: failure('[red bold]INVALID[/red bold] Reduce tournament duration, or increase game clock')
            valid = False
        if self.team_pm_template and len(self.team_pm_template):
            matches = re.findall(TemplateReplacement.TIMEZONE.value, self.team_pm_template)
            for tzmatch in matches:
                try:
                    ZoneInfo(tzmatch.replace('[timezone:', '').replace(']', ''))
                except ZoneInfoNotFoundError:
                    if with_output: failure(f'[red bold]INVALID[/red bold] Invalid timezone: {escape(tzmatch)}')
                    valid = False
        if self.type == TournamentType.Swiss and self.team_restriction is None:
            if with_output: failure('[red bold]INVALID[/red bold] Swiss tournaments must be restricted to a team')
            valid = False
        if self.type == TournamentType.TeamBattle:
            if self.team_restriction is None or len(self.team_restriction.split(',')) <= 1:
                if with_output: failure('[red bold]INVALID[/red bold] Team battles must have at least 2 teams')
                valid = False
            if self.num_leaders <= 0:
                if with_output: failure('[red bold]INVALID[/red bold] Team battles must have at least 1 leader per team')
                valid = False
        return valid

    def get_name(self, previous_winner: str):
        winner = '' if not previous_winner else ''.join([c for c in previous_winner if c.isalnum()])
        name = self.name.replace(NameReplacement.WINNER.value, winner).replace('  ', ' ').strip()
        if len(name) > 30:
            without_winner = self.name.replace(NameReplacement.WINNER.value, '').replace('  ', ' ').strip()
            alpha_chars = ''.join([c for c in previous_winner if c.isalpha()])
            name = self.name.replace(NameReplacement.WINNER.value, alpha_chars).replace('  ', ' ').strip()
            if len(name) > 30:
                diff = 30 - len(without_winner) - 1
                sub = alpha_chars[:diff]
                if len(sub) / len(alpha_chars) > 0.5:
                    return self.name.replace(NameReplacement.WINNER.value, sub).replace('  ', ' ').strip()
                else:
                    return without_winner
        return name

    def get_pm_message(self, created: TournamentResponse):
        if not self.team_pm_template or not self.team_restriction:
            return None
        message = self.team_pm_template
        message = message.replace(TemplateReplacement.NAME.value, created.full_name)
        message = message.replace(TemplateReplacement.VARIANT.value, self.variant.value)
        message = message.replace(TemplateReplacement.CLOCKTIME.value, self.clock_time.value)
        message = message.replace(TemplateReplacement.INCREMENT.value, self.clock_increment.value)
        message = message.replace(TemplateReplacement.LINK.value, f'https://lichess.org/tournament/{created.id}')
        message = message.replace(TemplateReplacement.BREAK.value, '\n')
        matches = re.findall(TemplateReplacement.TIMEZONE.value, message)
        starts_at = self.get_next_date()
        for tzmatch in matches:
            tz = ZoneInfo(tzmatch.replace('[timezone:', '').replace(']', ''))
            localized = starts_at.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S (%Z)')
            message = message.replace(tzmatch, localized)
        return message

    def needs_notification(self):
        if not self.team_pm_template or not self.team_restriction:
            return False
        utc_now = datetime.now(timezone.utc)
        next_date = self.get_next_date()
        if (next_date - utc_now).days > 0:
            return False
        return self.last_notified is None or (next_date - self.last_notified).days > 1
        

def tournament_json_serializer(obj):
    if isinstance(obj, Tournament):
        return obj.__dict__
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def tournament_json_decoder(data):
    enum_mappings = {
        'type': TournamentType,
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
    if data['last_notified']:
        data['last_notified'] = datetime.fromisoformat(data['last_notified'])
    return Tournament(**data)

def save_tournaments(tourneys: List[Tournament]):
    with open(constants.TOURNAMENTS_FILENAME, 'w') as tourneysFile:
        tourneysFile.write(json.dumps(tourneys, default=tournament_json_serializer, indent=4))

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