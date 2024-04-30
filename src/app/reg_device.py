from uuid import uuid4
from common.response import response
import json
from common.user_data import UserData


def lambda_handler(event, context):
    """Handles /regDevice POST requests."""
    # TODO: ip/deviceid/appkey rate limits
    client_ip = event['requestContext']['identity']['sourceIp']
    # TODO: handle input errors
    body = json.loads(event['body'])
    device_id = body['deviceID']
    user_token = uuid4()
    try: 
        UserData().create(user_token.bytes, ip=client_ip)
    except Exception as e:
        return response(e, None)
    return response(None, {'token': user_token.hex})
