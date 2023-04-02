from datetime import datetime
from models.RecurrenceType import RecurrenceType
from models.lichess.ClockTime import ClockTime
from models.lichess.ClockIncrement import ClockIncrement
from models.lichess.GamesRestriction import GamesRestriction
from models.lichess.RatingRestriction import RatingRestriction
from models.lichess.TournamentLength import TournamentLength
from models.lichess.Variant import Variant

class Tournament:
    def __init__(self,
                 name: str,
                 clock_time: ClockTime,
                 clock_increment: ClockIncrement,
                 length: TournamentLength,
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
        self.length_mins = length
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