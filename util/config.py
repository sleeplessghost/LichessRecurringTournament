import json
import util.constants as constants

def read():
    try:
        with open(constants.CONFIG_FILENAME, 'r') as configFile:
            config = json.loads(configFile.read())
            if constants.CONFIG_API_KEY not in config or constants.CONFIG_NUM_DAYS not in config:
                raise Warning('Required config is missing')
            if not isinstance(config[constants.CONFIG_API_KEY], str) or not isinstance(config[constants.CONFIG_NUM_DAYS], int):
                raise Warning('Config is misconfigured')
            return config
    except:
        print('Config file not found or misconfigured, try running the setup command')
        return None

def write(api_key: str, num_days: int):
    config = {constants.CONFIG_API_KEY: api_key, constants.CONFIG_NUM_DAYS: num_days}
    with open(constants.CONFIG_FILENAME, 'w') as configFile:
        configFile.write(json.dumps(config))