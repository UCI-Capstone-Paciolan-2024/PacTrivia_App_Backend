import datetime
import json

from common.scoring import calculate_score
from common.response import response
from common.user_data import UserData
from common.logger import getLogger


def lambda_handler(event, context):
    """Handles /checkAnswer POST requests."""
    body = json.loads(event['body'])
    logger = getLogger("checkAnswer")
    token = body.get('token', None)
    if type(token) is str:
        token = bytes.fromhex(token)
    ans = body.get('answer_index', -1)
    try:
        userdata = UserData()
        stat = userdata.check_answer(token, ans, datetime.datetime.utcnow())
        return_data = {'subtotal': stat['session_score'],
                       'answer_correct': stat['correct'],
                       'session_finished': stat['was_last'],
                       'elapsed_seconds': stat['elapsed_s'],
                       'prev_attempt_count': stat['attempt_no']}
        if stat['correct']:
            question_score = calculate_score(stat['max_s'], stat['elapsed_s'], 100, stat['attempt_no'])
            userdata.update_score(token, question_score)
            return_data['question_score'] = question_score
            return_data['subtotal'] += question_score
        else:
            return_data['question_score'] = 0
        return response(None, return_data)

    except Exception as e:
        return response(e)