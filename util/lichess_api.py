import json
from typing import List
import requests
from models.Templating import NameReplacement
from models.Tournament import Tournament
from models.TournamentType import TournamentType
from models.lichess.GamesRestriction import GamesRestriction
from models.lichess.RatingRestriction import RatingRestriction
from models.lichess.TournamentResponse import TournamentResponse
from models.lichess.Variant import Variant
from util.funi import failure, wait

BASE_URL = 'https://lichess.org'

def username(api_key: str) -> str:
    url = f'{BASE_URL}/api/account'
    profile = json.loads(rate_limited_get(url, api_key))
    return profile['username']

def teams(api_key: str, username: str) -> List[str]:
    url = f'{BASE_URL}/api/team/of/{username}'
    teams_data = json.loads(rate_limited_get(url, api_key))
    return [team['id'] for team in teams_data if is_leader(username, team)]

def my_tournaments(api_key: str, username: str) -> List[TournamentResponse]:
    url = f'{BASE_URL}/api/user/{username}/tournament/created?status=10'
    created = rate_limited_get(url, api_key).strip()
    if len(created) == 0: return []
    return [parse_created_tournament(json.loads(t)) for t in created.split('\n')]

def create_tournament(api_key: str, tournament: Tournament) -> TournamentResponse:
    teams = tournament.team_restriction.split(',')
    url = get_new_tournament_url(tournament.type, teams[0])
    name = tournament.get_name('')
    if tournament.last_id and NameReplacement.WINNER.value in tournament.name:
        prev_winner = tournament_winner(api_key, tournament.last_id)
        name = tournament.get_name(prev_winner)
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
    if len(name):
        data['name'] = name
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
        if tournament.team_restriction != None and tournament.type == TournamentType.Arena:
            conditions['teamMember.teamId'] = tournament.team_restriction
    if tournament.type == TournamentType.TeamBattle:
        data['teamBattleByTeam'] = tournament.team_restriction.split(',')[0]
        response = rate_limited_post(url, api_key, data)
        tournament_id = json.loads(response)['id']
        update_team_tournament(api_key, tournament_id, teams, tournament.num_leaders)
        return parse_created_tournament(json.loads(response))
    else:
        response = rate_limited_post(url, api_key, data)
        return parse_created_tournament(json.loads(response))

def update_team_tournament(api_key: str, tournament_id: str, teams: List[str], num_leaders: int):
    url = f'{BASE_URL}/api/tournament/team-battle/{tournament_id}'
    data = {
        'teams': ','.join(teams),
        'nbLeaders': num_leaders
    }
    rate_limited_post(url, api_key, data)

def pm_team(api_key: str, team_id: str, message: str):
    url = f'{BASE_URL}/team/{team_id}/pm-all'
    data = {'message': message}
    rate_limited_post(url, api_key, data)

def tournament_winner(api_key: str, tournament_id: str) -> str:
    if tournament_id is None: return ''
    url = f'{BASE_URL}/api/tournament/{tournament_id}/results?nb=1'
    results = rate_limited_try_get(url, api_key)
    if results is None or len(results.strip()) == 0: return ''
    return json.loads(results)['username']

def auth_header(api_key: str) -> dict:
    return {'Authorization': f'Bearer {api_key}'}

def rate_limited_get(url: str, api_key: str) -> str:
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

def rate_limited_try_get(url: str, api_key: str) -> str:
    response = requests.get(url, headers=auth_header(api_key))
    if response.ok:
        return response.text
    elif response.status_code == 429:
        failure('Request was rate limited, waiting for 1 min to retry')
        wait(60)
        return rate_limited_try_get(url, api_key)
    else:
        return None

def rate_limited_post(url: str, api_key: str, data: dict) -> str:
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
    id = jsonObj['id']
    full_name = jsonObj['fullName']
    return TournamentResponse(id, full_name)

def is_leader(username: str, teamJson) -> bool:
    leaders = [leaderJson['name'] for leaderJson in teamJson['leaders']]
    return username in leaders

def get_new_tournament_url(type: TournamentType, team_id: str):
    match type:
        case TournamentType.Arena | TournamentType.TeamBattle: return f'{BASE_URL}/api/tournament'
        case TournamentType.Swiss: return f'{BASE_URL}/api/swiss/new/{team_id}'