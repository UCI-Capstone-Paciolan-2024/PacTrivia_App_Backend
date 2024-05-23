import json
from common.response import response
from common.game_data import GameData


def lambda_handler(event, context):
    """Handles /questionManager POST requests."""
    body = json.loads(event['body'])
    # TODO: Admin authentication
    action = body['action']
    try:
        gd = GameData()
        if action == 'add':
            new_games = body['data']
            for g in new_games:
                gd.add(g['venue_id'], g['games'])
            return response(None, None)
        elif action == 'list':
            return response(None, gd.list(venue_id=body.get('venue_id', None)))
        elif action == 'remove':
            raise NotImplementedError()
        else:
            raise Exception("No or invalid 'action' received.")
    except Exception as e:
        return response(e)