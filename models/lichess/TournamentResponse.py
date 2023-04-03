
import json


class TournamentResponse:
    def __init__(self, name: str, rated: bool, clock_increment: int, starts_at_ms: int, variant: str):
        self.name = name
        self.rated = rated
        self.clock_increment = clock_increment
        self.starts_at_ms = starts_at_ms
        self.variant = variant

    def describe(self):
        return json.dumps(self.__dict__)