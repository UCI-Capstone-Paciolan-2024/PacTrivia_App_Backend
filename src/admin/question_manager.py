import json
from common.response import response
from common.question_data import QuestionData
from common.logger import getLogger


def lambda_handler(event, context):
    """Handles /questionManager POST requests."""
    body = json.loads(event['body'])
    logger = getLogger("questionManager")
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
        elif action == 'list_teams':
            # TODO: figure out a way to not need scan operation for this
            questions = qd.list()
            teams = {}
            for q in questions:
                if q['sk'] == 'meta':
                    teams[q['team']] = q.get('logo', None)
            return response(None, teams)
        elif action == 'update_logos':
            if len(teams := body.get('data')):
                for team, logo in teams.items():
                    qd.update_logo(team, logo)
                return response(None, None)
        elif action == 'remove':
            raise NotImplementedError()
        else:
            raise Exception("No or invalid 'action' received.")
    except Exception as e:
        logger.error(e)
        return response(e)