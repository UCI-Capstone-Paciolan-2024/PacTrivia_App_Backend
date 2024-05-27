from common.exceptions import QueryError, AuthError, AnswerTimeoutError, NoValidSessionError
from packages.botocore.exceptions import ClientError
import os
import datetime
from hashlib import sha256
from common.logger import getLogger
from common import dynamodb


class UserData:
    """Wrapper for user DynamoDB table queries"""
    def __init__(self, logger=getLogger("UserData")):
        self.logger = logger
        try:
            self.table = dynamodb.resource.Table(os.environ["USER_TABLE"])
            self.table.load()
        except ClientError as e:
            self.logger.error(f"Error loading user data table ({os.environ["USER_TABLE"]}): {e}")
            raise QueryError("Failed to load user table")

    def get(self, token: bytes) -> dict:
        """Return a complete user entry or throws error."""
        try:
            if len(token) != 16:
                self.logger.error(f"user token received is of invalid size {len(token)}, should be 16.")
                raise AuthError("Invalid token")
            hashed = sha256(token)
        except Exception as e:
            self.logger.error(f"failed to hash user token received: {e}")
            raise AuthError("Failed to hash token")
        try:
            dbresponse = self.table.get_item(Key={"pk": hashed.digest()})
        except ClientError as e:
            self.logger.error(f"Query to get user item failed: {e}")
            raise QueryError("User data query failed")
        self.logger.info(f"DynamoDB response to get user query: {dbresponse}")
        if item := dbresponse.get('Item'):
            return item
        self.logger.error(f"No user found for hashed token {hashed}")
        raise AuthError("Non-existent token")

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
            self.logger.error(f"Error saving new user {hashed.hexdigest()} to DB: {e}")
            raise QueryError("Failed to save user")
        self.logger.info(f"Saved new user with pk {hashed.hexdigest()}")

    def start_session(self, token: bytes, game: dict, assigned_questions: [], ip="") -> None:
        """Start a new game session for the specific user and event combo."""
        # TODO: enforce session limits
        hashed = sha256(token)
        self.logger.info(f"starting session for user {hashed.digest()}")
        try:
            old = self.table.update_item(
                Key={"pk": hashed.digest()},
                UpdateExpression="set last_ip=:i, session_data=:s",
                ExpressionAttributeValues={
                    ":i": ip, ":s": {"game": game,
                                     "started": datetime.datetime.utcnow().isoformat(),
                                     "question_counter": 0,
                                     "pending_score": 0,
                                     "questions": assigned_questions
                                     }
                },
                ReturnValues="UPDATED_OLD"
            )
        except ClientError as e:
            self.logger.error(f"Error saving session to DB: {e}")
            raise QueryError("Failed to save session")

    def retry_session(self, token: bytes, ip=""):
        """Restart session with the same questions, resetting score but imposing penalty."""
        hashed = sha256(token)
        self.logger.info(f"restarting session for user {hashed.hexdigest()}")
        try:
            old = self.table.update_item(
                Key={"pk": hashed.digest()},
                UpdateExpression="set last_ip=:i, #s.#cter=:zero, #s.#score=:zero, #s.#att=if_not_exists(#s.#att, :zero) + :one",
                ExpressionAttributeNames={
                    '#s': 'session_data',
                    '#cter': 'question_counter',
                    '#score': 'session_score',
                    '#att': 'attempt_no'
                },
                ExpressionAttributeValues={
                    ":i": ip, ":zero": 0, ":one": 1
                },
                ReturnValues="UPDATED_OLD",
            )
        except ClientError as e:
            self.logger.error(f"Error saving session to DB: {e}")
            raise QueryError("Failed to update session")

    def update_last_question_sent(self, token: bytes, q: dict):
        """"""
        hashed = sha256(token)
        self.logger.info(f"incrementing session question counter {hashed.hexdigest()}")
        try:
            old = self.table.update_item(
                Key={"pk": hashed.digest()},
                UpdateExpression="set #s.#wt=:wt, #s.#cter=if_not_exists(#s.#cter, :zero) + :one, #s.#qt=:qt, #seen.#team=list_append(if_not_exists(#seen.#team, :empty), :qsk)",
                ExpressionAttributeNames={
                    '#s': 'session_data',
                    '#cter': 'question_counter',
                    '#qt': 'question_time',
                    '#seen': 'questions_seen',
                    '#team': q['team'],
                    '#wt': 'awaiting_answer',
                },
                ExpressionAttributeValues={
                    ":zero": 0,
                    ":one": 1,
                    ":qt": datetime.datetime.utcnow().isoformat(),
                    ":qsk": [q['sk']],
                    ":empty": [],
                    ':wt': True,
                },
                ReturnValues="UPDATED_OLD",
            )
        except ClientError as e:
            self.logger.error(f"Error incrementing user question count : {e}")
            raise QueryError("Failed to update session")

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
            self.logger.error(f"Error updating user session in DB: {e}")
            raise QueryError("Failed to update session")

    def check_answer(self, token: bytes, selected: int, timestamp: datetime) -> dict:
        """Return the stats needed to score a response."""
        try:
            if user := self.get(token):
                self.logger.info("Found user")
                if session_data := user.get('session_data'):
                    self.logger.info("Found session")
                    attempt_data = {}
                    timeout = 30 # TODO: don't hardcode
                    question = user['session_data']['questions'][int(session_data['question_counter']) - 1]
                    self.logger.info("Found question")
                    if not user['session_data']['awaiting_answer']:
                        raise AnswerTimeoutError("Duplicate answer")
                    attempt_data['elapsed_s'] = (timestamp - datetime.datetime.fromisoformat(user['session_data']['question_time'])).seconds
                    if attempt_data['elapsed_s'] > timeout:
                        raise AnswerTimeoutError()
                    attempt_data['correct'] = selected in question['correct_indices']
                    attempt_data['max_s'] = timeout
                    attempt_data['session_score'] = int(user['session_data']['pending_score'])
                    attempt_data['was_last'] = user['session_data']['question_counter'] == user['session_data']['game']['questions_per_session']
                    attempt_data['attempt_no'] = int(user['session_data'].get('attempt_no', 0))
                    self.logger.info(f"Pre-scoring results: {attempt_data}")
                    return attempt_data
                raise NoValidSessionError()
            raise AuthError()
        except ClientError as e:
            self.logger.error(f"Error checking answer: {e}")
            raise QueryError("Failed to check answer")

    def update_score(self, token: bytes, increment_amount: int):
        """Add increment_amount to session (not final) score."""
        hashed = sha256(token)
        try:
            old = self.table.update_item(
                Key={"pk": hashed.digest()},
                UpdateExpression="set #ses.#wt=:wt, #ses.#sc=if_not_exists(#ses.#sc, :zero) + :inc",
                ExpressionAttributeNames={
                    '#ses': 'session_data',
                    '#sc': 'pending_score',
                    '#wt': 'awaiting_answer'
                },
                ExpressionAttributeValues={
                    ":inc": increment_amount,
                    ":zero": 0,
                    ":wt": False,
                },
                ReturnValues="UPDATED_OLD"
            )
            self.logger.info(f"incremented session score by {increment_amount}")
        except ClientError as e:
            self.logger.error(f"Error updating session score: {e}")
            raise QueryError("Failed to update score")

    def complete_session(self, token: bytes):
        """Add session score to final score, then delete session data. (reattempts not possible after this)"""
        hashed = sha256(token)
        try:
            old = self.table.update_item(
                Key={"pk": hashed.digest()},
                UpdateExpression="set score = score + if_not_exists(#ses.#sc, :zero) remove #ses",
                ExpressionAttributeNames={
                    '#ses': 'session_data',
                    '#sc': 'pending_score'
                },
                ExpressionAttributeValues={
                    ":zero": 0
                },
                ReturnValues="UPDATED_OLD"
            )
            self.logger.info(f"cleared last session and updated user score")
        except ClientError as e:
            self.logger.error(f"Failed to terminate/complete last session : {e}")
            raise QueryError("Failed to terminate/complete last session")

    def terminate_session(self):
        """Terminate a session even if not expired, discarding score."""
        raise NotImplementedError()
