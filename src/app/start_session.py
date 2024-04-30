import json
from common.response import response
from common.game_data import GameData
from common.user_data import UserData
from common.venue_data import VenueData


def lambda_handler(event, context):
    """Handles /startSession POST requests."""
    body = json.loads(event['body'])
    token = body.get('token', None)
    if type(token) is str:
        token = bytes.fromhex(token)
    location = body.get('userLocation',
                        ("33.65049375601106, -117.8470197846565"))  # Default to UCI for testing; TODO: remove this
    try:
        # find the closest venue with a game right now
        game = None
        for venue in sorted(VenueData().find_nearby(location), key=lambda x: x['distance']):
            game = GameData().now_playing(venue_id=venue['id'])
            if game:
                break
        # save the session
        UserData().start_session(token, game)
        return response(None, {'game': game})
    except Exception as e:
        return response(e)
