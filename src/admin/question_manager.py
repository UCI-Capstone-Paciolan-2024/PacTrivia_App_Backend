import json
from common.response import response
from common.question_data import QuestionData


def lambda_handler(event, context):
    """Handles /questionManager POST requests."""
    body = json.loads(event['body'])
    # TODO: Admin authentication
    action = body['action']
    qd = QuestionData()
    try:
        if action == 'add':
            new_questions = body['data']
            for q in new_questions:
                qd.add(team=q['team'], qas=q['questions'])
            return response(None, None)
        elif action == 'list':
            return response(None, qd.list(team=body.get('team',)))
        elif action == 'remove':
            raise NotImplementedError()
        else:
            raise Exception("No or invalid 'action' received.")
    except Exception as e:
        return response(e)