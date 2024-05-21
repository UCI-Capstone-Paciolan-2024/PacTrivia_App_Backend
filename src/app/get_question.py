import datetime
import json
import random
from common.response import response
from common.question_data import QuestionData
from common.user_data import UserData
from common.exceptions import NoValidSessionError


def lambda_handler(event, context):
    """Handles /getQuestion POST requests."""
    body = json.loads(event['body'])
    token = body.get('token', None)
    client_ip = event['requestContext']['identity']['sourceIp']
    if type(token) is str:
        token = bytes.fromhex(token)
    try:
        userdata = UserData()
        user = userdata.get(token)
        print(user)
        if session_data:= user.get('session_data', None):
            if (datetime.datetime.utcnow().isoformat() < session_data['game']['end']
                    and session_data['game']['questions_per_session'] > session_data['question_counter']):
                # pick one of the teams randomly
                team = random.sample(session_data['game']['teams'], 1)[0]
                seen = user['questions_seen'].get('team', None)
                last = -1
                if seen:
                    last = seen[-1]
                q = QuestionData().get_next(team, last)
                q['timeout_seconds'] = 30  # TODO: hardcoded value
                userdata.mark_question_seen(token, q, client_ip)
                return response(None, {
                    "question": q['question'],
                    "options": q['answer_options'],
                    "timeout_seconds": q['timeout_seconds'],
                })
        return response(NoValidSessionError())

    except Exception as e:
        return response(e)

