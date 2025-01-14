import json
import util.constants as constants
from util.funi import failure

class Config:
    def __init__(self, api_key: str, num_days: int):
        self.api_key = api_key
        self.num_days = num_days

    def save(self):
        with open(constants.CONFIG_FILENAME, 'w') as configFile:
            configFile.write(json.dumps(self.__dict__, indent=4))

def load_config() -> Config:
    try:
        with open(constants.CONFIG_FILENAME, 'r') as configFile:
            loaded = Config(**json.loads(configFile.read()))
            if not isinstance(loaded.api_key, str) or not isinstance(loaded.num_days, int):
                raise Warning('Config is misconfigured')
            return loaded
    except:
        failure('Config file not found or misconfigured, try running the setup command')
        quit()