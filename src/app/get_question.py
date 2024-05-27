import datetime
import json
import random
from common.response import response
from common.question_data import QuestionData
from common.user_data import UserData
from common.exceptions import NoValidSessionError
from common.logger import getLogger


def lambda_handler(event, context):
    """Handles /getQuestion POST requests."""
    body = json.loads(event['body'])
    token = body.get('token', None)
    logger = getLogger("getQuestion")
    client_ip = event['requestContext']['identity']['sourceIp']
    if type(token) is str:
        token = bytes.fromhex(token)
    logger.info(f"Received request for question from ip {client_ip}")
    try:
        userdata = UserData(logger=logger)
        user = userdata.get(token)
        logger.info(f"found user: {user}")
        if session_data:= user.get('session_data', None):
            if (datetime.datetime.utcnow().isoformat() < session_data['game']['end']
                    and session_data['game']['questions_per_session'] > session_data['question_counter']):
                q = session_data['questions'][int(session_data['question_counter'])]
                q['timeout_seconds'] = 30  # TODO: hardcoded value
                userdata.update_last_question_sent(token, q)
                return response(None, {
                    "question": q['question'],
                    "options": q['answer_options'],
                    "timeout_seconds": q['timeout_seconds'],
                })
            raise NoValidSessionError("Session finished")
        raise NoValidSessionError("No active session found")
    except Exception as e:
        return response(e)

