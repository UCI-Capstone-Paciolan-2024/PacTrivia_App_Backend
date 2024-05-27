import json
from common.response import response
from common.exceptions import NoGameFoundError, AuthError, NoValidSessionError
from common.game_data import GameData
from common.user_data import UserData
from common.venue_data import VenueData
from common.question_data import QuestionData
from common.logger import getLogger


def lambda_handler(event, context):
    """Handles /startSession POST requests."""
    logger = getLogger("startSession")
    body = json.loads(event['body'])
    token = body.get('token', None)
    if type(token) is str:
        token = bytes.fromhex(token)
    logger.info(f"Received user location: {body.get('userLocation')}")
    location = body.get('userLocation',
                        ("33.65049375601106, -117.8470197846565"))  # Default to UCI for testing; TODO: remove this
    ud = UserData(logger=logger)
    try:
        if user := ud.get(token):
            # find the closest venue with a game right now
            if not (game := body.get('override_game', None)):
                for venue in sorted(VenueData(logger=logger).find_nearby(location), key=lambda x: x['distance']):
                    game = GameData(logger=logger).now_playing(venue_id=venue['id'])
                    if game:
                        logger.info(f"Found nearest game: {game}")
                        break
            # generate a set of questions and save; return game info
            if game:
                if body.get('retry', False):
                    if not user.get('session_data', None):
                        raise NoValidSessionError("Could not find session to reattempt questions from.")
                    ud.retry_session(token)
                else:
                    teams = [{'name': team, 'meta': QuestionData().get_team_meta(team), 'exclude_sks': set(int(sk) for sk in user['questions_seen'].get(team, []))} for team in game['teams']]
                    logger.info(f"Team data for question selection: {teams}")
                    if not game.get('team_logos', None):
                        game['team_logos'] = [team['meta'].get('logo', None) for team in teams]
                    questions = QuestionData().get_random_set(teams, int(game['questions_per_session']))
                    logger.info(f"Questions assigned for session: {questions}")
                    if user.get('session_data', None) and not body.get('retry', False):
                        ud.complete_session(token)
                    ud.start_session(token, game, questions)
                    logger.info(f"Started user session")
                return response(None,{'game': game})
            raise NoGameFoundError("Could not find any nearby venue with an ongoing game.")
        raise AuthError()
    except Exception as e:
        logger.error(e)
        return response(e)
