import json
from common.response import response
from common.question_data import QuestionData


def lambda_handler(event, context):
    """Handles /addQuestions POST requests."""
    body = json.loads(event['body'])
    # TODO: Admin authentication
    try:
        new_questions = body['data']
        qd = QuestionData()
        for q in new_questions:
            qd.add(team=q['team'], qas=q['questions'])
    except Exception as e:
        return response(e)
    return response(None, None)