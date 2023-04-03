import json
from typing import List
import requests
from models.Tournament import Tournament
from models.lichess.GamesRestriction import GamesRestriction
from models.lichess.RatingRestriction import RatingRestriction
from models.lichess.TournamentResponse import TournamentResponse
from models.lichess.Variant import Variant
from util.funi import failure, wait

BASE_URL = 'https://lichess.org/api'

def username(api_key: str) -> str:
    url = f'{BASE_URL}/account'
    profile = json.loads(rate_limited_get(url, api_key))
    return profile['username']

def teams(api_key: str, username: str) -> List[str]:
    url = f'{BASE_URL}/team/of/{username}'
    teams_data = json.loads(rate_limited_get(url, api_key))
    return [team['id'] for team in teams_data]

def my_tournaments(api_key: str, username: str):
    url = f'{BASE_URL}/user/{username}/tournament/created?status=10'
    created = rate_limited_get(url, api_key).strip().split('\n')
    return [parse_created_tournament(json.loads(t)) for t in created]

def create_tournament(api_key: str, tournament: Tournament):
    url = f'{BASE_URL}/tournament'
    data = {
        'clockTime' : tournament.clock_time.float_val(),
        'clockIncrement': tournament.clock_increment.int_val(),
        'minutes': tournament.length_mins.int_val(),
        'startDate': int(tournament.get_next_date().timestamp() * 1000),
        'variant': tournament.variant.value,
        'rated': tournament.rated,
        'berserkable': tournament.berserkable,
        'streakable': tournament.streakable,
        'hasChat': tournament.has_chat,
        'description': tournament.description,
    }
    if len(tournament.name):
        data['name'] = tournament.name
    if tournament.variant == Variant.FROM_POSITION:
        data['position'] = tournament.positionFEN
    if tournament.has_restrictions():
        conditions = data['conditions'] = {}
        if tournament.min_rating != RatingRestriction.NONE:
            conditions['minRating.rating'] = tournament.min_rating.int_val()
        if tournament.max_rating != RatingRestriction.NONE:
            conditions['maxRating.rating'] = tournament.max_rating.int_val()
        if tournament.min_games != GamesRestriction.NONE:
            conditions['nbRatedGame.nb'] = tournament.min_games.int_val()
        if tournament.team_restriction != None:
            conditions['teamMember.teamId'] = tournament.team_restriction
    rate_limited_post(url, api_key, data)

def auth_header(api_key: str):
    return {'Authorization': f'Bearer {api_key}'}

def rate_limited_get(url: str, api_key: str):
    response = requests.get(url, headers=auth_header(api_key))
    if response.ok:
        return response.text
    elif response.status_code == 429:
        failure('Request was rate limited, waiting for 1 min to retry')
        wait(60)
        return rate_limited_get(url, api_key)
    else:
        message = f'Web request failed: {response.status_code} - {response.reason}'
        if response.status_code == 401: message = '401 Unauthorized - have you run setup with the correct API key?'
        failure(message)
        quit()

def rate_limited_post(url: str, api_key: str, data: dict):
    response = requests.post(url, headers=auth_header(api_key), json=data)
    if response.ok:
        return response.text
    elif response.status_code == 429:
        failure('Request was rate limited, waiting for 1 min to retry')
        wait(60)
        return rate_limited_post(url, api_key, data)
    else:
        message = f'Web request failed: {response.status_code} - {response.reason}'
        if response.status_code == 401: message = '401 Unauthorized - have you run setup with the correct API key?'
        failure(message)
        quit()

def parse_created_tournament(jsonObj) -> TournamentResponse:
    name = jsonObj['fullName']
    rated = jsonObj['rated']
    increment = jsonObj['clock']['increment']
    starts_at_ms = jsonObj['startsAt']
    variant = jsonObj['variant']['key']
    return TournamentResponse(name, rated, increment, starts_at_ms, variant)