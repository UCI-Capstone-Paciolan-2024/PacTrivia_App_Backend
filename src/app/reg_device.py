from uuid import uuid4
from common.response import response
import json
from common.user_data import UserData
from common.logger import getLogger


def lambda_handler(event, context):
    """Handles /regDevice POST requests."""
    logger = getLogger("regDevice")
    # TODO: ip/deviceid/appkey rate limits
    client_ip = event['requestContext']['identity']['sourceIp']
    # TODO: handle input errors
    body = json.loads(event['body'])
    device_id = body['deviceID']
    logger.info(f"Received request to register device {device_id} from ip {client_ip}")
    user_token = uuid4()
    try: 
        UserData(logger=logger).create(user_token.bytes, ip=client_ip)
        logger.info(f"Created account for device {device_id}")
    except Exception as e:
        return response(e, None)
    return response(None, {'token': user_token.hex})
