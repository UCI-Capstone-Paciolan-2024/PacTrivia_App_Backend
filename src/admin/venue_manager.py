import json
from common.response import response
from common.venue_data import VenueData


def lambda_handler(event, context):
    """Handles /questionManager POST requests."""
    body = json.loads(event['body'])
    # TODO: Admin authentication
    action = body['action']
    if action == 'add':
        try:
            new_venues = body['data']
            vd = VenueData()
            for v in new_venues:
                vd.add(v['name'], v['coords'])
        except Exception as e:
            return response(e)
        return response(None, None)
    elif action == 'list':
        return response(NotImplementedError())
    elif action == 'remove':
        return response(NotImplementedError())
    else:
        return response(Exception("No or invalid 'action' received."))