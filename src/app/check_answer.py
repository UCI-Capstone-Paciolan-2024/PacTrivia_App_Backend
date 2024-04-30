import datetime
import json

from common.scoring import calculate_score
from common.response import response
from common.user_data import UserData


def lambda_handler(event, context):
    """Handles /checkAnswer POST requests."""
    body = json.loads(event['body'])
    token = body.get('token', None)
    if type(token) is str:
        token = bytes.fromhex(token)
    ans = body.get('answer_index', -1)
    client_time = body.get('client_time')  # not used for now
    try:
        userdata = UserData()
        stat = userdata.check_answer(token, ans, datetime.datetime.utcnow().isoformat())
        return_data = {'subtotal': stat['session_score']}
        if stat['correct']:
            question_score = calculate_score(stat['max_s'], stat['elapsed_s'], 100, stat['attempt_no'])
            userdata.update_score(token, question_score)
            return_data['question_score'] = question_score
            return_data['subtotal'] += question_score
        else:
            return_data['question_score'] = 0
        return return_data

    except Exception as e:
        return response(e)