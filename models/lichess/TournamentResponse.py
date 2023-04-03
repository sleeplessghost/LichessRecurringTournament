
import json


class TournamentResponse:
    def __init__(self, id: str, name: str, full_name: str, rated: bool, clock_increment: int, starts_at_ms: int, variant: str, required_team: str):
        self.id = id
        self.name = name
        self.full_name = full_name
        self.rated = rated
        self.clock_increment = clock_increment
        self.starts_at_ms = starts_at_ms
        self.variant = variant
        self.required_team = required_team

    def describe(self):
        return json.dumps(self.__dict__)