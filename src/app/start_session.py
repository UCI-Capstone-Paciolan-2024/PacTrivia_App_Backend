import json
from common.response import response
from common.game_data import GameData
from common.user_data import UserData
from common.venue_data import VenueData
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
    try:
        # find the closest venue with a game right now
        game = None
        for venue in sorted(VenueData().find_nearby(location), key=lambda x: x['distance']):
            game = GameData(logger=logger).now_playing(venue_id=venue['id'])
            if game:
                logger.info(f"Found nearby game: {game}")
                break
        # save the session
        UserData(logger=logger).start_session(token, game)
        logger.info(f"Started user session")
        return response(None, {'game': game})
    except Exception as e:
        logger.error(e)
        return response(e)
