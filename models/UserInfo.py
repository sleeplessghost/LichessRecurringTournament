import json
from typing import List
import util.constants as constants
from util.funi import failure

class UserInfo:
    def __init__(self, username: str, teams: List[str] = []):
        self.username = username
        self.teams = teams

    def add_team(self, team_id: str):
        if team_id not in self.teams:
            self.teams.push(team_id)

    def remove_team(self, team_id: str):
        if team_id in self.teams:
            self.teams.remove(team_id)

    def save(self):
        with open(constants.USER_INFO_FILENAME, 'w') as userFile:
            userFile.write(json.dumps(self.__dict__, indent=4))

def load_user_info() -> UserInfo:
    try:
        with open(constants.USER_INFO_FILENAME, 'r') as userFile:
            loaded = UserInfo(**json.loads(userFile.read()))
            if not isinstance(loaded.username, str) or not isinstance(loaded.teams, list):
                raise Warning('User info is misconfigured')
            return loaded
    except:
        failure('User info file not found or misconfigured, try running the refresh command')
        quit()