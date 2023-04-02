import json
import requests
from util.funi import failure, wait

BASE_URL = 'https://lichess.org/api'

def username(api_key: str):
    url = f'{BASE_URL}/account'
    profile = rate_limited_get(url, api_key)
    return profile['username']

def teams(api_key: str, username: str):
    url = f'{BASE_URL}/team/of/{username}'
    teams_data = rate_limited_get(url, api_key)
    return [team['id'] for team in teams_data]

def auth_header(api_key: str):
    return {'Authorization': f'Bearer {api_key}'}

def rate_limited_get(url: str, api_key: str):
    response = requests.get(url, headers=auth_header(api_key))
    if response.ok:
        return json.loads(response.text)
    elif response.status_code == 429:
        failure('Request was rate limited, waiting for 1 min to retry')
        wait(60)
        return rate_limited_get(url, api_key)
    else:
        failure(f'Web request failed: {response.status_code} - {response.reason}')
        quit()