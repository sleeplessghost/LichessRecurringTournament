import json
import typer

app = typer.Typer()
config_filename = "config.json"
config_api_key = "ApiKey"
config_num_days = "NumDays"

@app.command()
def setup(api_key: str = typer.Option(..., prompt="Enter your Lichess API key"), num_days: int = typer.Option(..., prompt="How many days in the future should tournaments be created?")):
    """
    Setup config file
    """
    config = {config_api_key: api_key, config_num_days: num_days}
    with open(config_filename, 'w') as configFile:
        configFile.write(json.dumps(config))
    

@app.command()
def refresh():
    """
    Refresh lichess information (teams you can access)
    """
    print("refresh")

@app.command()
def create():
    """
    Creates configured tournaments within the next X days (from config file)
    """
    print("create")

@app.command()
def new():
    """
    Configure a new recurring tournament
    """
    print("new")

@app.command()
def list():
    """
    Lists configured tournaments
    """
    print("list")

@app.command()
def delete(id: int):
    """
    Deletes a configured tournament
    """
    print("delete")

def readConfig():
    try:
        with open(config_filename, 'r') as configFile:
            config = json.loads(configFile.read())
            if config_api_key not in config or config_num_days not in config:
                raise Warning('Required config is missing')
            if not isinstance(config[config_api_key], str) or not isinstance(config[config_num_days], int):
                raise Warning('Config is misconfigured')
            return config
    except:
        print('Config file not found or misconfigured, try running the setup command')
        return None

if __name__ == "__main__":
    app()