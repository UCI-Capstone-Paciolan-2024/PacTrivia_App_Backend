from common.exceptions import QueryError, AuthError, AnswerTimeoutException, NoValidSessionError
from packages.botocore.exceptions import ClientError
import os
import datetime
from hashlib import sha256
from common import dynamodb


class UserData:
    """Wrapper for user DynamoDB table queries"""
    def __init__(self):
        try:
            self.table = dynamodb.resource.Table(os.environ["USER_TABLE"])
            self.table.load()
        except ClientError as e:
            print(e)
            raise QueryError()

    def get(self, token: bytes) -> dict:
        """Return a complete user entry or throws error."""
        try:
            if len(token) != 16:
                print("Invalid user token size")
                raise AuthError()
            hashed = sha256(token)
        except Exception as e:
            print(f"Failed to hash user token")
            raise AuthError()
        try:
            dbresponse = self.table.get_item(Key={"pk": hashed.digest()})
        except ClientError as e:
            raise QueryError()
        if item := dbresponse.get('Item'):
            return item
        raise AuthError()

    def create(self, token: bytes, ip="", username="Anonymous") -> None:
        """Create a new user entry."""
        hashed = sha256(token)
        try: 
            self.table.put_item(
                Item={
                    'pk': hashed.digest(),
                    'score': 0,
                    'username': username,
                    'last_ip': ip,
                    'questions_seen': {} # team:[question_sk]
                }
            )
        except ClientError as e:
            print(f"Error saving user to DB: {e}")
            raise QueryError()

    def start_session(self, token: bytes, game: dict, ip="") -> None:
        """Start a new game session for the specific user and event combo."""
        # TODO: enforce session limits
        hashed = sha256(token)
        try:
            old = self.table.update_item(
                Key={"pk": hashed.digest()},
                UpdateExpression="set last_ip=:i, session_data=:s",
                ExpressionAttributeValues={
                    ":i": ip, ":s": {"game": game,
                                     "started": datetime.datetime.utcnow().isoformat(),
                                     "question_counter": 0,
                                     "pending_score": 0,
                                     }
                },
                ReturnValues="UPDATED_OLD"
            )
        except ClientError as e:
            print(f"Error saving session to DB: {e}")
            raise QueryError()

    def mark_question_seen(self, token: bytes, question: dict, ip: str) -> None:
        """Update user entry to track the last sent question."""
        hashed = sha256(token)
        try:
            old = self.table.update_item(
                Key={"pk": hashed.digest()},
                UpdateExpression="set #ip=:i,"
                                 "#seen.#team=list_append(if_not_exists(#seen.#team, :empty), :qsk),"
                                 "#ses.#qct=if_not_exists(#ses.#qct, :zero) + :one,"
                                 "#ses.#pq=:q,"
                                 "#ses.#qt=:qt",
                ExpressionAttributeNames={
                    '#ip': 'last_ip',
                    '#seen': 'questions_seen',
                    '#ses': 'session_data',
                    '#qct': 'question_counter',
                    '#pq': 'pending_question',
                    '#qt': 'question_time',
                    '#team': question['team']
                },
                ExpressionAttributeValues={
                    ":i": ip,
                    ":zero": 0,
                    ":one": 1,
                    ":empty": [],
                    ":qsk": [question['sk']],
                    ":q": question,
                    ":qt": datetime.datetime.utcnow().isoformat(),
                },
                ReturnValues="UPDATED_OLD"
            )
        except ClientError as e:
            print(f"Error updating user session: {e}")
            raise QueryError()

    def check_answer(self, token: bytes, selected: int, timestamp: datetime) -> dict:
        """Return the values needed to score a response."""
        try:
            if user := self.get(token):
                r = {}
                r['attempt_no'] = 0  # TODO
                r['elapsed_s'] = (timestamp - datetime.datetime.fromisoformat(user['session_data']['question_time'])).seconds
                if r['elapsed_s'] > user['pending_question']['timeout_seconds']:
                    raise AnswerTimeoutException()
                r['correct'] = selected in user['session_data']['pending_question']['correct_indices']
                r['max_s'] = user['session_data']['pending_question']['timeout_seconds']
                r['session_score'] = user['session_data']['pending_score']
                r['is_last'] = user['session_data']['question_counter'] == user['session_data']['game']['questions_per_session']
                return r
            raise AuthError()
        except ClientError as e:
            print(f"Error checking answer: {e}")
            raise QueryError()

    def update_score(self, token: bytes, increment_amount: int):
        """Add increment_amount to session (not final) score."""
        raise NotImplementedError()

    def complete_session(self, token: bytes):
        """Add session score to final score, then delete session data."""
        raise NotImplementedError()

    def terminate_session(self):
        """Terminate a session even if not expired, discarding score."""
        raise NotImplementedError()
